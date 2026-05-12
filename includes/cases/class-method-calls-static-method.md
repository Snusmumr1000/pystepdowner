### Instance method caller -> one static method callee

Caller: one instance method. Callees: one static method. Expected order: caller first, then callee.

Before:

```python
--8<-- "docs_src/cases/class_method_calls_static_method/before.py"
```

After:

```python
--8<-- "docs_src/cases/class_method_calls_static_method/after.py"
```
