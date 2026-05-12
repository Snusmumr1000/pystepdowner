### Function A calls B then C

`pystepdowner` keeps called functions below the caller in call order.

Before:

```python
--8<-- "docs_src/cases/function_a_calls_b_then_c/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_a_calls_b_then_c/after.py"
```
