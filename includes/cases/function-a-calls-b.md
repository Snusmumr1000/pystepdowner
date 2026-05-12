### Function caller -> one function callee

Caller: one module-level function. Callees: one module-level function. Expected order: caller first, then callee.

Before:

```python
--8<-- "docs_src/cases/function_a_calls_b/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_a_calls_b/after.py"
```
