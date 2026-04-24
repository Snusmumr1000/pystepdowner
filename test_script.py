import ast
from pystepdowner.analyzer import process_body

source = """@deco
def b():
    pass
# Comment for a
def a():
    b()
"""
lines = source.splitlines()
tree = ast.parse(source)
for stmt in tree.body:
    print(stmt.name, stmt.lineno, stmt.end_lineno)
