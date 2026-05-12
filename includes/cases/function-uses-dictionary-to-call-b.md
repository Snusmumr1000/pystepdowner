### Function subject -> one function reference via dictionary value

Subject: one module-level function. References: one module-level function. Reference form: dictionary value selected by argument key. Expected order: subject first, then referenced declaration.

Before:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b/before.py"
```

After:

```python
--8<-- "docs_src/cases/function_uses_dictionary_to_call_b/after.py"
```
