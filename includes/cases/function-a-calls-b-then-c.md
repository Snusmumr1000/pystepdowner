### Function subject -> two function references via direct calls

Subject: one module-level function. References: two module-level functions. Reference form: direct calls. Expected order: subject first, then referenced declarations in reference order.

Before:

```python
--8<-- "docs_src/cases/function_a_calls_b_then_c/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_a_calls_b_then_c/after.py"
```
