### Instance method subject -> instance method and static method references via direct calls

Subject: one instance method. References: one instance method and one static method. Reference form: direct calls. Expected order: subject first, then referenced declarations in reference order.

Before:

```python
--8<-- "docs_src/cases/class_method_calls_instance_and_static_methods/before.py"
```

After:

```python
--8<-- "docs_src/cases/class_method_calls_instance_and_static_methods/after.py"
```
