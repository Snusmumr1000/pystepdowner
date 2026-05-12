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

## Function A calls B then C

`pystepdowner` keeps called functions below the caller in call order.

Before:

```python
def c() -> str:
    return "c"


def b() -> str:
    return "b"


def a() -> str:
    return b() + c()
```

After:

```python
def a() -> str:
    return b() + c()


def b() -> str:
    return "b"


def c() -> str:
    return "c"
```
