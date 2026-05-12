### Class method subject -> one class method reference via direct call

Subject: one class method. References: one class method. Reference form: direct call through `cls`. Expected order: subject first, then referenced declaration.

Before:

```python
--8<-- "docs/docs_src/cases/classmethod_calls_classmethod/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/classmethod_calls_classmethod/after.py"
```
