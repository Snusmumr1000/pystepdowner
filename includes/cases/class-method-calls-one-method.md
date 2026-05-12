### Instance method subject -> one instance method reference via direct call

Subject: one instance method. References: one instance method. Reference form: direct call. Expected order: subject first, then referenced declaration.

Before:

```python
--8<-- "docs_src/cases/class_method_calls_one_method/before.py"
```

After:

```python
--8<-- "docs_src/cases/class_method_calls_one_method/after.py"
```
