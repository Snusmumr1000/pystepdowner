### Function caller -> two function callees through dictionary dispatch

Caller: one module-level function with dictionary dispatch by argument key. Callees: two module-level functions referenced in the dictionary. Expected order: caller first, then callees in dictionary insertion order.

Before:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b_and_c/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b_and_c/after.py"
```
