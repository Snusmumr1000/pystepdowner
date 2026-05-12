### Instance method subject -> one static method reference via direct call

Subject: one instance method. References: one static method. Reference form: direct call. Expected order: subject first, then referenced declaration.

Before:

```python
--8<-- "docs/docs_src/cases/class_method_calls_static_method/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/class_method_calls_static_method/after.py"
```
