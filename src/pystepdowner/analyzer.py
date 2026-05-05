import ast
import heapq

from pystepdowner.models import NodeChunk


def reformat_content(content: str) -> str:
    tree = ast.parse(content)
    lines = content.splitlines()

    new_lines, modified, needs_future = process_body(tree.body, lines)

    if needs_future:
        has_future = any(line.strip() == "from __future__ import annotations" for line in new_lines)
        if not has_future:
            insert_idx = 0
            if tree.body:
                first_stmt = tree.body[0]
                if (
                    isinstance(first_stmt, ast.Expr)
                    and isinstance(first_stmt.value, ast.Constant)
                    and isinstance(first_stmt.value.value, str)
                ):
                    insert_idx = first_stmt.end_lineno
            new_lines.insert(insert_idx, "from __future__ import annotations")
            new_lines.insert(insert_idx + 1, "")
            new_lines.insert(insert_idx + 2, "")
            modified = True

    if modified:
        return "\n".join(new_lines) + "\n" if new_lines else ""

    return content


def get_calls(node: ast.AST, class_name: str | None) -> set[str]:
    calls = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            calls.add(child.id)
        elif (
            isinstance(child, ast.Attribute)
            and isinstance(child.value, ast.Name)
            and (child.value.id in ("self", "cls") or (class_name and child.value.id == class_name))
        ):
            calls.add(child.attr)
    return calls


def get_annotation_calls(node: ast.AST, class_name: str | None) -> set[str]:
    annotation_nodes = []
    for child in ast.walk(node):
        if isinstance(child, ast.arg) and child.annotation:
            annotation_nodes.append(child.annotation)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.returns:
            annotation_nodes.append(child.returns)
        elif isinstance(child, ast.AnnAssign) and child.annotation:
            annotation_nodes.append(child.annotation)

    calls = set()
    for ann_node in annotation_nodes:
        for child in ast.walk(ann_node):
            if isinstance(child, ast.Name):
                calls.add(child.id)
            elif (
                isinstance(child, ast.Attribute)
                and isinstance(child.value, ast.Name)
                and (child.value.id in ("self", "cls") or (class_name and child.value.id == class_name))
            ):
                calls.add(child.attr)
    return calls


def extract_chunks(
    nodes: list[ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef], lines: list[str], prev_node_end_line: int, class_name: str | None
) -> tuple[list[NodeChunk], int, int]:
    chunks = []
    group_start_idx = -1
    group_end_idx = -1

    for i, node in enumerate(nodes):
        start_lineno = node.lineno
        if getattr(node, "decorator_list", []):
            start_lineno = min(d.lineno for d in node.decorator_list)
        end_lineno = node.end_lineno
        if end_lineno is None:
            end_lineno = start_lineno

        start_idx = start_lineno - 1
        end_idx = end_lineno - 1

        limit = prev_node_end_line if i == 0 else nodes[i - 1].end_lineno
        if limit is None:
            limit = 0

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


def reorder_chunks(chunks: list[NodeChunk]) -> list[NodeChunk]:
    chunk_by_name = {c.name: c for c in chunks}

    in_degree: dict[str, int] = {c.name: 0 for c in chunks}
    for c in chunks:
        for call in c.calls:
            if call in in_degree:
                in_degree[call] += 1

    inits = []
    others = []
    for c in chunks:
        if c.is_init:
            inits.append(c)
        else:
            others.append(c)

    inits.sort(key=lambda c: 0 if c.name == "__init__" else 1)

    others_in_degree: dict[str, int] = {c.name: 0 for c in others}
    for c in others:
        local_calls = [call for call in c.calls if call in chunk_by_name]
        for call in local_calls:
            others_in_degree[call] += 1

    roots = [c for c in others if others_in_degree[c.name] == 0]
    roots.sort(key=lambda c: len([call for call in c.calls if call in chunk_by_name]), reverse=True)

    root_index_map = {c.name: 999999 for c in others}
    level_map = {c.name: 999999 for c in others}

    for i, root in enumerate(roots):
        queue_bfs = [(root.name, 0)]
        visited_bfs = set()
        while queue_bfs:
            curr, depth = queue_bfs.pop(0)

            if i < root_index_map[curr]:
                root_index_map[curr] = i

            if depth < level_map[curr]:
                level_map[curr] = depth

            if curr in visited_bfs:
                continue
            visited_bfs.add(curr)

            c = chunk_by_name[curr]
            queue_bfs.extend([(call, depth + 1) for call in c.calls if call in chunk_by_name])

    queue: list[tuple[int, int, str, NodeChunk]] = []
    for c in others:
        if others_in_degree[c.name] == 0:
            heapq.heappush(queue, (root_index_map[c.name], level_map[c.name], c.name, c))

    ordered: list[NodeChunk] = []
    while queue:
        _, _, _, c = heapq.heappop(queue)
        ordered.append(c)
        local_calls = [call for call in c.calls if call in chunk_by_name]
        for call in local_calls:
            others_in_degree[call] -= 1
            if others_in_degree[call] == 0:
                child_c = chunk_by_name[call]
                heapq.heappush(queue, (root_index_map[call], level_map[call], call, child_c))

    ordered_names = {c.name for c in ordered}
    for c in others:
        if c.name not in ordered_names:
            ordered.append(c)

    return inits + ordered


def process_body(body: list[ast.stmt], lines: list[str], class_name: str | None = None) -> tuple[list[str], bool, bool]:
    new_lines = lines[:]
    modified = False
    needs_future = False

    for stmt in body:
        if isinstance(stmt, ast.ClassDef):
            class_lines, class_mod, class_needs_future = process_body(stmt.body, new_lines, class_name=stmt.name)
            if class_mod:
                new_lines = class_lines
                modified = True
            if class_needs_future:
                needs_future = True

    groups = []
    current_group = []

    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            current_group.append(stmt)
        else:
            if len(current_group) > 1:
                groups.append(current_group)
            current_group = []

    if len(current_group) > 1:
        groups.append(current_group)

    # We must process groups from bottom to top so that replacing lines doesn't shift the indices of earlier groups!
    groups.reverse()

    for group in groups:
        # Find the statement immediately before this group to set the limit
        # This is a bit tricky since we reversed the groups. We need to find the node before group[0] in the original body.
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

        seen = set()
        for c in reordered:
            seen.add(c.name)
            for ann_call in c.annotation_calls:
                if ann_call in new_order and ann_call not in seen:
                    needs_future = True

        if original_order != new_order:
            modified = True
            separator = ["", ""] if class_name is None else [""]

            # Preserve the leading blank lines from the original first chunk
            # (they represent spacing between preceding code and this group)
            original_prefix: list[str] = []
            first_chunk_lines = chunks[0].lines
            for line in first_chunk_lines:
                if line.strip():
                    break
                original_prefix.append(line)

            reordered_lines: list[str] = list(original_prefix)
            for i, c in enumerate(reordered):
                # Strip leading blank lines from each chunk
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
