Nested scopes are reordered independently, preserving the same top-down reading flow inside the outer function.

Before:

```python
--8<-- "docs/docs_src/cases/function_contains_nested_function_references/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/function_contains_nested_function_references/after.py"
```
