The caller moves above the helpers it uses. Function bodies are lazy, so helpers may safely be defined below the caller.

Before:

```python
--8<-- "docs/docs_src/cases/function_references/before.py"
```

After:

```python
--8<-- "docs/docs_src/cases/function_references/after.py"
```
