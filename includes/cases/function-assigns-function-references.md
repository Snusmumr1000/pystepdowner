### Function subject -> two function references via list values

Subject: one module-level function. References: two module-level functions. Reference form: list values returned without calling. Expected order: subject first, then referenced declarations in list insertion order.

Before:

```python
--8<-- "docs_src/cases/function_assigns_function_references/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_assigns_function_references/after.py"
```
