### Function subject -> self reference and helper reference via direct calls

Subject: one recursive module-level function. References: itself and one module-level helper function. Reference form: direct calls. Expected order: subject first, then referenced helper declarations in reference order.

Before:

```python
--8<-- "docs_src/cases/function_calls_recursive_function_and_helper/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_calls_recursive_function_and_helper/after.py"
```
