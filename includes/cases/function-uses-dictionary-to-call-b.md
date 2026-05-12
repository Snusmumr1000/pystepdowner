### Function caller -> one function callee through dictionary dispatch

Caller: one module-level function with dictionary dispatch by argument key. Callees: one module-level function referenced in the dictionary. Expected order: caller first, then callee.

Before:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b/after.py"
```
