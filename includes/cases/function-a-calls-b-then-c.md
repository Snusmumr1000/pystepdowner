### Function caller -> two function callees

Caller: one module-level function. Callees: two module-level functions. Expected order: caller first, then callees in call order.

Before:

```python
--8<-- "docs_src/cases/function_a_calls_b_then_c/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_a_calls_b_then_c/after.py"
```
