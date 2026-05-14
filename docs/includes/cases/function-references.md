### Function subjects - 1:N -> Function reference

Subject: one module-level function. References: one or more module-level functions. Reference form: lazy evaluation. Expected order: subject first, then referenced declarations in their first appearance order.

Before:

```python
--8<-- "docs/docs_src/cases/function_references/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/function_references/after.py"
```
