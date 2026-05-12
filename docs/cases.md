# Cases

## Function A calls B

`pystepdowner` moves called functions below their caller.

Before:

```python
def b() -> str:
    return "b"


def a() -> str:
    return b()
```

After:

```python
def a() -> str:
    return b()


def b() -> str:
    return "b"
```
