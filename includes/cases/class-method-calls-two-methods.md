### Instance method caller -> two instance method callees

Caller: one instance method. Callees: two instance methods. Expected order: caller first, then callees in call order.

Before:

```python
--8<-- "docs_src/cases/class_method_calls_two_methods/before.py"
```

After:

```python
--8<-- "docs_src/cases/class_method_calls_two_methods/after.py"
```
