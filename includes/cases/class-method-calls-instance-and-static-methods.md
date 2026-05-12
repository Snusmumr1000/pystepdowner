### Instance method caller -> instance method and static method callees

Caller: one instance method. Callees: one instance method and one static method. Expected order: caller first, then callees in call order.

Before:

```python
--8<-- "docs_src/cases/class_method_calls_instance_and_static_methods/before.py"
```

After:

```python
--8<-- "docs_src/cases/class_method_calls_instance_and_static_methods/after.py"
```
