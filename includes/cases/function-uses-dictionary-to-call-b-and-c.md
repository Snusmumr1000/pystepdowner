### Function subject -> two function references via dictionary values

Subject: one module-level function. References: two module-level functions. Reference form: dictionary values selected by argument key. Expected order: subject first, then referenced declarations in dictionary insertion order.

Before:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b_and_c/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b_and_c/after.py"
```
