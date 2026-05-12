### Instance method subject -> two instance method references via direct calls

Subject: one instance method. References: two instance methods. Reference form: direct calls. Expected order: subject first, then referenced declarations in reference order.

Before:

```python
--8<-- "docs/docs_src/cases/class_method_calls_two_methods/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/class_method_calls_two_methods/after.py"
```
