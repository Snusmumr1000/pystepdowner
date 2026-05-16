import ast
import itertools
from collections.abc import Callable, Iterable, Iterator
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
                calls, ann, eager = _extract_calls(node)
                starts.append(s)
                chunks.append(
                    NodeChunk(
                        name=cast(Any, node).name,
                        is_init=cast(Any, node).name in ("__init__", "__post_init__"),
                        lines=new_lines[s : e + 1],
                        calls=calls,
                        annotation_calls=ann,
                        eager_calls=eager,
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

            target_len = end_idx - start_idx + 1
            if len(rebuilt) < target_len:
                rebuilt.extend([""] * (target_len - len(rebuilt)))
            elif len(rebuilt) > target_len:
                while len(rebuilt) > target_len and not rebuilt[-1].strip():
                    rebuilt.pop()

            new_lines[start_idx : end_idx + 1] = rebuilt

    return new_lines, modified, needs_future


def _extract_calls(node: ast.AST) -> tuple[list[str], list[str], list[str]]:
    cls = next((getattr(p, "name", None) for p in _walk_parents(node) if isinstance(p, ast.ClassDef)), None)

    def get_pos(n: ast.AST, ignore_class_assigns: bool) -> tuple[int, int, str] | None:
        if isinstance(getattr(n, "ctx", None), (ast.Store, ast.Del)):
            return None
        if ignore_class_assigns and isinstance(getattr(n, "parent", None), ast.Assign):
            in_func = any(isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)) for p in _walk_parents(n))
            if not in_func:
                return None
        if isinstance(n, ast.Name):
            return n.lineno, n.col_offset, n.id
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in ("self", "cls", cls):
            return n.lineno, n.col_offset, n.attr
        return None

    all_pos: list[tuple[int, int, str]] = []
    ann_pos: list[tuple[int, int, str]] = []
    eager_pos = _extract_eager_positions(node, get_pos)
    for child in ast.walk(node):
        if pos := get_pos(child, True):
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
                if pos_ann := get_pos(n, True):
                    ann_pos.append(pos_ann)

    def dedup(items: Iterable[tuple[int, int, str]]) -> list[str]:
        return list(dict.fromkeys(name for _, _, name in sorted(items)))

    eager = set(dedup(eager_pos))
    return [name for name in dedup(all_pos) if name not in eager], dedup(ann_pos), dedup(eager_pos)


def _walk_parents(node: ast.AST) -> Iterator[ast.AST]:
    cur = getattr(node, "parent", None)
    while cur:
        yield cur
        cur = getattr(cur, "parent", None)


def _extract_eager_positions(
    node: ast.AST,
    get_pos: Callable[[ast.AST, bool], tuple[int, int, str] | None],
) -> list[tuple[int, int, str]]:
    targets: list[ast.AST] = []

    def add_function_eager(func: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        targets.extend(func.decorator_list)
        targets.extend(func.args.defaults)
        targets.extend(default for default in func.args.kw_defaults if default is not None)

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        add_function_eager(node)
    elif isinstance(node, ast.ClassDef):
        targets.extend(node.decorator_list)
        targets.extend(node.bases)
        targets.extend(keyword.value for keyword in node.keywords)
        for stmt in node.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                add_function_eager(stmt)
            elif not isinstance(stmt, ast.ClassDef):
                targets.extend(_class_body_eager_targets(stmt))

    eager_pos: list[tuple[int, int, str]] = []
    for target in targets:
        for child in ast.walk(target):
            if pos := get_pos(child, False):
                eager_pos.append(pos)
    return eager_pos


def _class_body_eager_targets(stmt: ast.stmt) -> list[ast.AST]:
    if isinstance(stmt, ast.Assign):
        return [stmt.value]
    if isinstance(stmt, ast.AnnAssign):
        return [stmt.value] if stmt.value else []
    if isinstance(stmt, ast.AugAssign):
        return [stmt.value]
    if isinstance(stmt, ast.Expr):
        return [stmt.value]
    if isinstance(stmt, (ast.For, ast.AsyncFor)):
        return [stmt.iter, *stmt.body, *stmt.orelse]
    if isinstance(stmt, ast.With):
        targets: list[ast.AST] = [item.context_expr for item in stmt.items]
        targets.extend(stmt.body)
        return targets
    if isinstance(stmt, ast.AsyncWith):
        targets = [item.context_expr for item in stmt.items]
        targets.extend(stmt.body)
        return targets
    if isinstance(stmt, ast.If):
        return [stmt.test, *stmt.body, *stmt.orelse]
    return [stmt]


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
        for eager in node.eager_calls:
            if eager in cmap and eager != node.name and eager not in visited:
                _dfs(cmap[eager])
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
