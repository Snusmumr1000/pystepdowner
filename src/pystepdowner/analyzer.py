import ast

from pystepdowner.models import NodeChunk


def reformat_content(content: str) -> str:
    tree = ast.parse(content)
    lines = content.splitlines()

    new_lines, modified, needs_future = process_body(tree.body, lines)

    if needs_future and not _has_future_annotations(new_lines):
        _prepend_future_annotations(tree, new_lines)
        modified = True

    if modified:
        return "\n".join(new_lines) + "\n" if new_lines else ""

    return content


def process_body(body: list[ast.stmt], lines: list[str], class_name: str | None = None) -> tuple[list[str], bool, bool]:
    new_lines, modified, needs_future = _recurse_class_bodies(body, lines)
    group_lines, group_mod, group_future = _process_function_groups(body, new_lines, class_name)

    if group_mod:
        new_lines = group_lines
        modified = True
    if group_future:
        needs_future = True

    return new_lines, modified, needs_future


def _recurse_class_bodies(body: list[ast.stmt], lines: list[str]) -> tuple[list[str], bool, bool]:
    new_lines = lines[:]
    modified = False
    needs_future = False

    for stmt in body:
        if isinstance(stmt, ast.ClassDef):
            class_lines, class_mod, class_future = process_body(stmt.body, new_lines, class_name=stmt.name)
            if class_mod:
                new_lines = class_lines
                modified = True
            if class_future:
                needs_future = True

    return new_lines, modified, needs_future


def _process_function_groups(body: list[ast.stmt], lines: list[str], class_name: str | None) -> tuple[list[str], bool, bool]:
    new_lines = lines[:]
    modified = False
    needs_future = False

    groups = _collect_groups(body)

    # Process bottom-to-top so that replacing lines doesn't shift indices of earlier groups.
    for group in reversed(groups):
        idx = body.index(group[0])
        prev_node_end_line = 0
        if idx > 0:
            prev = body[idx - 1]
            if hasattr(prev, "end_lineno") and prev.end_lineno is not None:
                prev_node_end_line = prev.end_lineno

        chunks, start_idx, end_idx = extract_chunks(group, new_lines, prev_node_end_line, class_name)
        reordered = reorder_chunks(chunks)

        original_order = [c.name for c in chunks]
        new_order = [c.name for c in reordered]

        seen: set[str] = set()
        for c in reordered:
            seen.add(c.name)
            for ann_call in c.annotation_calls:
                if ann_call in new_order and ann_call not in seen:
                    needs_future = True

        if original_order != new_order:
            modified = True
            separator = ["", ""] if class_name is None else [""]

            original_prefix: list[str] = []
            for line in chunks[0].lines:
                if line.strip():
                    break
                original_prefix.append(line)

            reordered_lines: list[str] = list(original_prefix)
            for i, c in enumerate(reordered):
                content_start = 0
                for j, line in enumerate(c.lines):
                    if line.strip():
                        content_start = j
                        break
                chunk_content = c.lines[content_start:]
                if i > 0:
                    reordered_lines.extend(separator)
                reordered_lines.extend(chunk_content)

            new_lines[start_idx : end_idx + 1] = reordered_lines

    return new_lines, modified, needs_future


def _collect_groups(body: list[ast.stmt]) -> list[list[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef]]:
    groups: list[list[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef]] = []
    current: list[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef] = []

    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            current.append(stmt)
        else:
            if len(current) > 1:
                groups.append(current)
            current = []

    if len(current) > 1:
        groups.append(current)

    return groups


def extract_chunks(
    nodes: list[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef],
    lines: list[str],
    prev_node_end_line: int,
    class_name: str | None,
) -> tuple[list[NodeChunk], int, int]:
    chunks = []
    group_start_idx = -1
    group_end_idx = -1

    for i, node in enumerate(nodes):
        start_lineno = node.lineno
        if getattr(node, "decorator_list", []):
            start_lineno = min(d.lineno for d in node.decorator_list)
        end_lineno = node.end_lineno or start_lineno

        start_idx = start_lineno - 1
        end_idx = end_lineno - 1

        limit = prev_node_end_line if i == 0 else (nodes[i - 1].end_lineno or 0)

        while start_idx > limit:
            line = lines[start_idx - 1].strip()
            if line == "" or line.startswith("#"):
                start_idx -= 1
            else:
                break

        if i == 0:
            group_start_idx = start_idx
        group_end_idx = end_idx

        chunk_lines = lines[start_idx : end_idx + 1]
        is_init = node.name in ("__init__", "__post_init__")

        calls = get_calls(node, class_name)
        annotation_calls = get_annotation_calls(node, class_name)
        chunks.append(NodeChunk(name=node.name, is_init=is_init, lines=chunk_lines, calls=calls, annotation_calls=annotation_calls))

    return chunks, group_start_idx, group_end_idx


def get_calls(node: ast.AST, class_name: str | None) -> list[str]:
    return _extract_ordered_calls([node], class_name)


def get_annotation_calls(node: ast.AST, class_name: str | None) -> list[str]:
    annotation_nodes = []
    for child in ast.walk(node):
        if isinstance(child, ast.arg) and child.annotation:
            annotation_nodes.append(child.annotation)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.returns:
            annotation_nodes.append(child.returns)
        elif isinstance(child, ast.AnnAssign) and child.annotation:
            annotation_nodes.append(child.annotation)

    return _extract_ordered_calls(annotation_nodes, class_name)


def _extract_ordered_calls(nodes: list[ast.AST], class_name: str | None) -> list[str]:
    calls_with_pos: list[tuple[int, int, str]] = []
    for node in nodes:
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                calls_with_pos.append((getattr(child, "lineno", 0), getattr(child, "col_offset", 0), child.id))
            elif isinstance(child, ast.Attribute) and _is_local_attribute(child, class_name):
                calls_with_pos.append((getattr(child, "lineno", 0), getattr(child, "col_offset", 0), child.attr))
                
    calls_with_pos.sort()

    seen: set[str] = set()
    result: list[str] = []
    for _, _, name in calls_with_pos:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def _is_local_attribute(node: ast.Attribute, class_name: str | None) -> bool:
    return isinstance(node.value, ast.Name) and (
        node.value.id in ("self", "cls") or (class_name is not None and node.value.id == class_name)
    )


def reorder_chunks(chunks: list[NodeChunk]) -> list[NodeChunk]:
    chunk_by_name = {c.name: c for c in chunks}

    inits = [c for c in chunks if c.is_init]
    others = [c for c in chunks if not c.is_init]

    inits.sort(key=lambda c: 0 if c.name == "__init__" else 1)

    # Compute in-degrees to identify roots (self-calls excluded).
    in_degree: dict[str, int] = {c.name: 0 for c in others}
    for c in others:
        for call in c.calls:
            if call in in_degree and call != c.name:
                in_degree[call] += 1

    # Find back-edges to break cycles for DAG-based deferral
    visiting: set[str] = set()
    visited_for_dag: set[str] = set()
    back_edges: set[tuple[str, str]] = set()

    def _find_back_edges(u_name: str) -> None:
        if u_name in visiting or u_name in visited_for_dag:
            return
        visiting.add(u_name)
        u_chunk = chunk_by_name[u_name]
        for v_name in u_chunk.calls:
            if v_name in chunk_by_name and v_name != u_name:
                if v_name in visiting:
                    back_edges.add((u_name, v_name))
                else:
                    _find_back_edges(v_name)
        visiting.remove(u_name)
        visited_for_dag.add(u_name)

    for c in others:
        _find_back_edges(c.name)

    # Compute DAG callers (excluding back-edges)
    dag_callers: dict[str, set[str]] = {c.name: set() for c in others}
    for c in others:
        for v_name in c.calls:
            if v_name in chunk_by_name and v_name != c.name:
                if (c.name, v_name) not in back_edges:
                    dag_callers[v_name].add(c.name)

    # Precompute reachability for sorting callees
    reachable: dict[str, set[str]] = {c.name: set() for c in others}
    for c in others:
        reachable[c.name].update(call for call in c.calls if call in chunk_by_name and call != c.name)
    
    changed = True
    while changed:
        changed = False
        for c in others:
            orig_len = len(reachable[c.name])
            for call in list(reachable[c.name]):
                if call in reachable:
                    reachable[c.name].update(reachable[call])
            if len(reachable[c.name]) > orig_len:
                changed = True

    # Roots sorted by descending local out-degree (broader callers first).
    def _root_sort_key(c: NodeChunk) -> tuple[int, int]:
        local_calls = sum(1 for call in c.calls if call in chunk_by_name and call != c.name)
        return (-local_calls, chunks.index(c))

    roots = sorted(
        [c for c in others if in_degree[c.name] == 0],
        key=_root_sort_key,
    )

    ordered: list[NodeChunk] = []
    visited: set[str] = set()

    def _dfs(node: NodeChunk) -> None:
        if node.name in visited:
            return
            
        unvisited_dag_callers = dag_callers[node.name] - visited
        if unvisited_dag_callers:
            return
            
        visited.add(node.name)
        ordered.append(node)
        # Visit callees depth-first. Primary callees first, then by source-code call order.
        callees = [chunk_by_name[call] for call in node.calls if call in chunk_by_name and call != node.name and call not in visited]
        
        callees_copy = list(callees)
        def _callee_sort_key(callee: NodeChunk) -> tuple[int, int]:
            reachable_from_others = sum(1 for other in callees_copy if other != callee and callee.name in reachable.get(other.name, set()))
            call_order = node.calls.index(callee.name) if callee.name in node.calls else 0
            return (reachable_from_others, call_order)

        callees.sort(key=_callee_sort_key)
        for callee in callees:
            _dfs(callee)

    for root in roots:
        _dfs(root)

    # Append any chunks not reached (e.g. isolated nodes with no root path)
    for c in others:
        if c.name not in visited:
            dag_callers[c.name].clear()
            _dfs(c)

    return inits + ordered


def _has_future_annotations(lines: list[str]) -> bool:
    return any(line.strip() == "from __future__ import annotations" for line in lines)


def _prepend_future_annotations(tree: ast.Module, lines: list[str]) -> None:
    insert_idx = 0
    if tree.body:
        first_stmt = tree.body[0]
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
            insert_idx = first_stmt.end_lineno or 0
    lines.insert(insert_idx, "from __future__ import annotations")
    lines.insert(insert_idx + 1, "")
    lines.insert(insert_idx + 2, "")
