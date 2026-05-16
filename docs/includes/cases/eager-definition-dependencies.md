Some expressions are evaluated immediately: decorators, default arguments, and class-body values. Those dependencies stay above the chunk that needs them, even when a lazy caller can move first.

Before:

```python
--8<-- "docs/docs_src/cases/eager_definition_dependencies/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/eager_definition_dependencies/after.py"
```
