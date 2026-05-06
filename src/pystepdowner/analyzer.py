import ast
import itertools
from collections.abc import Iterable, Iterator
from typing import Any, cast

from pystepdowner.models import NodeChunk

_FUNC_OR_CLASS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def reformat_content(content: str) -> str:
    tree = ast.parse(content)
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            cast(Any, child).parent = node

    new_lines, modified, needs_future = _process_body(tree.body, content.splitlines())

    if needs_future and not any(line.strip() == "from __future__ import annotations" for line in new_lines):
        idx = (
            (tree.body[0].end_lineno or 0)
            if tree.body
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)
            else 0
        )
        new_lines[idx:idx] = ["from __future__ import annotations", "", ""]
        modified = True

    return "\n".join(new_lines) + "\n" if modified and new_lines else content


def _process_body(body: list[ast.stmt], lines: list[str]) -> tuple[list[str], bool, bool]:
    new_lines, modified, needs_future = lines[:], False, False

    for stmt in body:
        if isinstance(stmt, _FUNC_OR_CLASS):
            new_lines, m, f = _process_body(stmt.body, new_lines)
            modified |= m
            needs_future |= f

    groups = []
    for is_func, grp in itertools.groupby(body, lambda s: isinstance(s, _FUNC_OR_CLASS)):
        if not is_func:
            continue

        curr = list(grp)
        if len(curr) > 1:
            idx = body.index(curr[0])
            limit = (getattr(body[idx - 1], "end_lineno", 0) or 0) if idx > 0 else 0
            chunks, starts = [], []
            for node in curr:
                d = getattr(node, "decorator_list", [])
                s, e = (min(x.lineno for x in d) if d else node.lineno) - 1, (node.end_lineno or node.lineno) - 1
                while s > limit and (not (line := new_lines[s - 1].strip()) or line.startswith("#")):
                    s -= 1
                limit = e + 1
                calls, ann = _extract_calls(node)
                starts.append(s)
                chunks.append(
                    NodeChunk(
                        name=cast(Any, node).name,
                        is_init=cast(Any, node).name in ("__init__", "__post_init__"),
                        lines=new_lines[s : e + 1],
                        calls=calls,
                        annotation_calls=ann,
                    )
                )
            groups.append((chunks, starts[0], limit - 1))

    for chunks, start_idx, end_idx in reversed(groups):
        reordered = reorder_chunks(chunks)
        orig, new = [c.name for c in chunks], [c.name for c in reordered]

        seen = set()
        for c in reordered:
            seen.add(c.name)
            if any(a in new and a not in seen for a in c.annotation_calls):
                needs_future = True

        if orig != new:
            modified = True
            sep = ["", ""] if body and isinstance(getattr(body[0], "parent", None), ast.Module) else [""]
            prefix = list(itertools.takewhile(lambda line: not line.strip(), chunks[0].lines))
            rebuilt = list(prefix)
            for i, c in enumerate(reordered):
                if i > 0:
                    rebuilt.extend(sep)
                rebuilt.extend(itertools.dropwhile(lambda line: not line.strip(), c.lines))
            new_lines[start_idx : end_idx + 1] = rebuilt

    return new_lines, modified, needs_future


def _extract_calls(node: ast.AST) -> tuple[list[str], list[str]]:
    cls = next((getattr(p, "name", None) for p in _walk_parents(node) if isinstance(p, ast.ClassDef)), None)

    def get_pos(n: ast.AST) -> tuple[int, int, str] | None:
        if isinstance(n.parent, ast.Assign):
            return None
        if isinstance(n, ast.Name):
            return n.lineno, n.col_offset, n.id
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in ("self", "cls", cls):
            return n.lineno, n.col_offset, n.attr
        return None

    all_pos: list[tuple[int, int, str]] = []
    ann_pos: list[tuple[int, int, str]] = []
    for child in ast.walk(node):
        if pos := get_pos(child):
            all_pos.append(pos)
        targets = []
        if isinstance(child, ast.arg) and child.annotation:
            targets.append(child.annotation)
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.returns:
            targets.append(child.returns)
        if isinstance(child, ast.AnnAssign) and child.annotation:
            targets.append(child.annotation)
        for t in targets:
            for n in ast.walk(t):
                if pos_ann := get_pos(n):
                    ann_pos.append(pos_ann)

    def dedup(items: Iterable[tuple[int, int, str]]) -> list[str]:
        return list(dict.fromkeys(name for _, _, name in sorted(items)))

    return dedup(all_pos), dedup(ann_pos)


def _walk_parents(node: ast.AST) -> Iterator[ast.AST]:
    cur = getattr(node, "parent", None)
    while cur:
        yield cur
        cur = getattr(cur, "parent", None)


def reorder_chunks(chunks: list[NodeChunk]) -> list[NodeChunk]:
    cmap = {c.name: c for c in chunks}
    inits = sorted((c for c in chunks if c.is_init), key=lambda c: c.name != "__init__")
    others = [c for c in chunks if not c.is_init]

    reach = {c.name: {x for x in c.calls if x in cmap and x != c.name} for c in others}
    for k in reach:
        for i in reach:
            if k in reach[i]:
                reach[i].update(reach[k])

    indeg = {c.name: sum(1 for o in others if c.name in o.calls and o.name != c.name) for c in others}
    roots = sorted(
        [c for c in others if not indeg[c.name]], key=lambda c: (-sum(1 for x in c.calls if x in cmap and x != c.name), chunks.index(c))
    )

    ordered, visited = [], set()

    def _dfs(node: NodeChunk) -> None:
        if node.name in visited:
            return
        if any(c.name != node.name and c.name not in visited and node.name in c.calls and c.name not in reach[node.name] for c in others):
            return
        visited.add(node.name)
        ordered.append(node)
        callees = [cmap[x] for x in node.calls if x in cmap and x != node.name and x not in visited]
        callees.sort(key=lambda c: (sum(1 for o in callees if c.name in reach[o.name]), node.calls.index(c.name)))
        for callee in callees:
            _dfs(callee)

    for r in roots:
        _dfs(r)
    for c in others:
        _dfs(c)
    return inits + ordered
