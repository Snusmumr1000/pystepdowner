### Function subject -> one function reference via direct call

Subject: one module-level function. References: one module-level function. Reference form: direct call. Expected order: subject first, then referenced declaration.

Before:

```python
--8<-- "docs/docs_src/cases/function_a_calls_b/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/function_a_calls_b/after.py"
```
