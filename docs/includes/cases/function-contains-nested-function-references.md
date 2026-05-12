### Function subject -> nested function references via direct calls

Subject: one module-level function containing local functions. References: nested local functions at multiple nesting levels. Reference form: direct calls. Expected order: each local subject first, then its referenced local declarations.

Before:

```python
--8<-- "docs/docs_src/cases/function_contains_nested_function_references/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/function_contains_nested_function_references/after.py"
```
