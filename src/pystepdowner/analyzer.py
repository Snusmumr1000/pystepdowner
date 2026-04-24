import ast

from pystepdowner.models import NodeChunk


def get_calls(node: ast.AST, class_name: str | None) -> set[str]:
    calls = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.add(child.func.id)
            elif isinstance(child.func, ast.Attribute) and isinstance(child.func.value, ast.Name):
                if child.func.value.id in ('self', 'cls') or (class_name and child.func.value.id == class_name):
                    calls.add(child.func.attr)
    return calls

def extract_chunks(
    nodes: list[ast.FunctionDef | ast.AsyncFunctionDef],
    lines: list[str],
    prev_node_end_line: int,
    class_name: str | None
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

        limit = prev_node_end_line if i == 0 else nodes[i-1].end_lineno
        if limit is None:
            limit = 0

        while start_idx > limit:
            line = lines[start_idx - 1].strip()
            if line == '' or line.startswith('#'):
                start_idx -= 1
            else:
                break

        if i == 0:
            group_start_idx = start_idx
        group_end_idx = end_idx

        chunk_lines = lines[start_idx:end_idx + 1]
        is_init = node.name in ('__init__', '__post_init__')
        
        calls = get_calls(node, class_name)
        chunks.append(NodeChunk(
            name=node.name,
            is_init=is_init,
            lines=chunk_lines,
            calls=calls
        ))

    return chunks, group_start_idx, group_end_idx

def reorder_chunks(chunks: list[NodeChunk]) -> list[NodeChunk]:
    chunk_by_name = {c.name: c for c in chunks}
    
    # Identify in-degrees to find roots
    in_degree: dict[str, int] = {c.name: 0 for c in chunks}
    for c in chunks:
        for call in c.calls:
            if call in in_degree:
                in_degree[call] += 1

    # Inits always go first
    inits = []
    others = []
    for c in chunks:
        if c.is_init:
            inits.append(c)
        else:
            others.append(c)
            
    inits.sort(key=lambda c: 0 if c.name == '__init__' else 1)
    
    roots = [c for c in others if in_degree[c.name] == 0]
    
    # Sort roots by out-degree (number of local calls) descending
    roots.sort(key=lambda c: len([call for call in c.calls if call in chunk_by_name]), reverse=True)
    
    ordered: list[NodeChunk] = []
    visited: set[str] = set()

    def visit(c: NodeChunk) -> None:
        if c.name in visited:
            return
        visited.add(c.name)
        ordered.append(c)
        
        # Visit children in the order they appear in the AST calls, or alphabetically? 
        # For simplicity and determinism, alphabetically.
        local_calls = sorted([call for call in c.calls if call in chunk_by_name])
        for call in local_calls:
            visit(chunk_by_name[call])

    for root in roots:
        visit(root)
        
    # Any isolated cycles or unreachable functions
    for c in others:
        if c.name not in visited:
            visit(c)

    return inits + ordered

def process_body(body: list[ast.stmt], lines: list[str], class_name: str | None = None) -> tuple[list[str], bool]:
    groups = []
    current_group = []
    
    new_lines = lines[:]
    modified = False

    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            current_group.append(stmt)
        else:
            if len(current_group) > 1:
                groups.append(current_group)
            current_group = []
            if isinstance(stmt, ast.ClassDef):
                # Process class body recursively
                class_lines, class_mod = process_body(stmt.body, new_lines, class_name=stmt.name)
                if class_mod:
                    new_lines = class_lines
                    modified = True

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
            if hasattr(prev, 'end_lineno') and prev.end_lineno is not None:
                prev_node_end_line = prev.end_lineno

        chunks, start_idx, end_idx = extract_chunks(group, new_lines, prev_node_end_line, class_name)
        
        reordered = reorder_chunks(chunks)
        
        original_order = [c.name for c in chunks]
        new_order = [c.name for c in reordered]
        
        if original_order != new_order:
            modified = True
            reordered_lines = []
            for c in reordered:
                reordered_lines.extend(c.lines)
            
            new_lines[start_idx:end_idx + 1] = reordered_lines

    return new_lines, modified

from pathlib import Path


def reformat_file(filepath: str) -> bool:
    path = Path(filepath)
    with path.open(encoding='utf-8') as f:
        source = f.read()
    
    lines = source.splitlines()
    tree = ast.parse(source)
    
    new_lines, modified = process_body(tree.body, lines)
    
    if modified:
        with path.open('w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines) + '\n')
            
    return modified
