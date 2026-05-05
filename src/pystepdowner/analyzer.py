import ast

from pystepdowner.models import NodeChunk


def reformat_content(content: str) -> str:
    tree = ast.parse(content)

    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    lines = content.splitlines()

    new_lines, modified, needs_future = process_body(tree.body, lines)

    if needs_future and not any(line.strip() == "from __future__ import annotations" for line in new_lines):
        _prepend_future_annotations(tree, new_lines)
        modified = True

    if modified:
        return "\n".join(new_lines) + "\n" if new_lines else ""

    return content


def process_body(body: list[ast.stmt], lines: list[str]) -> tuple[list[str], bool, bool]:
    new_lines = lines[:]
    modified = False
    needs_future = False

    # Recurse into class and function bodies
    for stmt in body:
        if isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            new_lines, m, f = process_body(stmt.body, new_lines)
            modified |= m
            needs_future |= f

    # Collect and reorder function groups
    for group in reversed(_collect_groups(body)):
        idx = body.index(group[0])
        prev_node_end_line = 0
        if idx > 0:
            prev = body[idx - 1]
            if hasattr(prev, "end_lineno") and prev.end_lineno is not None:
                prev_node_end_line = prev.end_lineno

        chunks, start_idx, end_idx = _extract_chunks(group, new_lines, prev_node_end_line)
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
            is_top_level = len(body) > 0 and isinstance(getattr(body[0], "parent", None), ast.Module)
            separator = ["", ""] if is_top_level else [""]

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


def _extract_chunks(
    nodes: list[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef],
    lines: list[str],
    prev_node_end_line: int,
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

        calls = _extract_calls(node, annotations_only=False)
        annotation_calls = _extract_calls(node, annotations_only=True)
        chunks.append(NodeChunk(name=node.name, is_init=is_init, lines=chunk_lines, calls=calls, annotation_calls=annotation_calls))

    return chunks, group_start_idx, group_end_idx


def _extract_calls(node: ast.AST, *, annotations_only: bool) -> list[str]:
    class_name = _get_enclosing_class_name(node)
    if annotations_only:
        targets: list[ast.AST] = []
        for child in ast.walk(node):
            if isinstance(child, ast.arg) and child.annotation:
                targets.append(child.annotation)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.returns:
                targets.append(child.returns)
            elif isinstance(child, ast.AnnAssign) and child.annotation:
                targets.append(child.annotation)
    else:
        targets = [node]

    calls_with_pos: list[tuple[int, int, str]] = []
    for target in targets:
        for child in ast.walk(target):
            if isinstance(child, ast.Name):
                calls_with_pos.append((getattr(child, "lineno", 0), getattr(child, "col_offset", 0), child.id))
            elif (
                isinstance(child, ast.Attribute)
                and isinstance(child.value, ast.Name)
                and (child.value.id in ("self", "cls") or (class_name is not None and child.value.id == class_name))
            ):
                calls_with_pos.append((getattr(child, "lineno", 0), getattr(child, "col_offset", 0), child.attr))

    calls_with_pos.sort()

    seen: set[str] = set()
    result: list[str] = []
    for _, _, name in calls_with_pos:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def _get_enclosing_class_name(node: ast.AST) -> str | None:
    current = getattr(node, "parent", None)
    while current:
        if isinstance(current, ast.ClassDef):
            return current.name
        current = getattr(current, "parent", None)
    return None


def reorder_chunks(chunks: list[NodeChunk]) -> list[NodeChunk]:
    chunk_map = {c.name: c for c in chunks}

    inits = [c for c in chunks if c.is_init]
    others = [c for c in chunks if not c.is_init]

    inits.sort(key=lambda c: 0 if c.name == "__init__" else 1)

    # In-degrees for root detection (self-calls excluded).
    in_deg: dict[str, int] = {c.name: 0 for c in others}
    for c in others:
        for call in c.calls:
            if call in in_deg and call != c.name:
                in_deg[call] += 1

    roots = sorted(
        [c for c in others if in_deg[c.name] == 0],
        key=lambda c: (-sum(1 for x in c.calls if x in chunk_map and x != c.name), chunks.index(c)),
    )

    ordered: list[NodeChunk] = []
    visited: set[str] = set()

    def _dfs(node: NodeChunk) -> None:
        if node.name in visited:
            return

        # Defer if an unvisited non-cyclic caller exists.
        for c in others:
            if c.name == node.name or c.name in visited:
                continue
            if node.name not in c.calls:
                continue
            # c calls node and is unvisited — defer unless it's a cycle
            if not _is_reachable(node.name, c.name, set()):
                return

        visited.add(node.name)
        ordered.append(node)

        callees = [chunk_map[x] for x in node.calls if x in chunk_map and x != node.name and x not in visited]
        callee_names = {c.name for c in callees}
        callees.sort(
            key=lambda c: (
                sum(1 for other in callee_names - {c.name} if _is_reachable(other, c.name, set())),
                node.calls.index(c.name),
            )
        )
        for callee in callees:
            _dfs(callee)

    def _is_reachable(src: str, dst: str, seen: set[str]) -> bool:
        """Check if dst is reachable from src in the call graph (cycle detection)."""
        if src == dst:
            return True
        if src in seen or src not in chunk_map:
            return False
        seen.add(src)
        for call in chunk_map[src].calls:
            if call in chunk_map and call != src and _is_reachable(call, dst, seen):
                return True
        return False

    for root in roots:
        _dfs(root)

    # Append any chunks not reached (isolated nodes or unresolved cycles).
    for c in others:
        if c.name not in visited:
            _dfs(c)

    return inits + ordered


def _prepend_future_annotations(tree: ast.Module, lines: list[str]) -> None:
    insert_idx = 0
    if tree.body:
        first_stmt = tree.body[0]
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
            insert_idx = first_stmt.end_lineno or 0
    lines.insert(insert_idx, "from __future__ import annotations")
    lines.insert(insert_idx + 1, "")
    lines.insert(insert_idx + 2, "")
