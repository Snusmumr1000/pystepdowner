### Function subject -> function references via lazy evaluation

Subject: one module-level function. References: two module-level functions. Reference form: lazy evaluation. Expected order: subject first, then referenced declarations in their first appearance order.

Before:

```python
--8<-- "docs/docs_src/cases/function_lazy_evaluation_references/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/function_lazy_evaluation_references/after.py"
```
