# pystepdowner

A tool to enforce the **Stepdown Rule** (from Uncle Bob's *Clean Code*) in your Python files.

The Stepdown Rule states that code should be readable from top to bottom. Every function should be followed by those at the next level of abstraction so that we can read the program, descending one level of abstraction at a time as we read down the list of functions.

`pystepdowner` analyzes your Python files and rearranges functions and methods to adhere to this rule, prioritizing source-code call order and correctly handling complex dependency graphs.

More example cases: https://Snusmumr1000.github.io/pystepdowner/

## References

- [The Stepdown Rule](https://dzone.com/articles/the-stepdown-rule)
- [Stepdown Rule](https://github.com/Geeksltd/Programming.Tips/blob/master/docs/methods/stepdown-rule.md)

## Installation

You can install `pystepdowner` as a global CLI tool using `uv` (recommended):

```bash
# Install from PyPI
uv tool install pystepdowner

# Or install from source locally
uv tool install .
```

Alternatively, you can install it into any Python environment using standard `pip`:

```bash
pip install pystepdowner
```

## Usage

The CLI provides two main commands: `fmt` and `rw`.

### 1. `fmt`: Format and Print to Output
Use the `fmt` command to format a single file and output the result to your terminal. This is useful for previewing changes without modifying the actual file.

```bash
pystepdowner fmt -i my_script.py
```

### 2. `rw`: Rewrite Files
Use the `rw` command to format and rewrite files. You can rewrite a single file or an entire directory recursively.

#### Rewrite a Single File In-Place
```bash
pystepdowner rw -i my_script.py
```

#### Rewrite a Single File and Save to a New Location
```bash
pystepdowner rw -i my_script.py -o formatted_script.py
```

#### Rewrite an Entire Directory In-Place
This will recursively find and format all `.py` files inside the target directory.

```bash
pystepdowner rw -i src/
```

## Example

`pystepdowner` transforms bottom-up code into top-down code, putting high-level logic before the helpers it calls.

**Before:**
```python
def load_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}


def format_user(user: dict) -> str:
    return f"{user['id']}: {user['name']}"


def user_controller(user_id: int) -> dict:
    user = load_user(user_id)
    return {"body": format_user(user)}
```

**After running `pystepdowner rw -i my_script.py`:**
```python
def user_controller(user_id: int) -> dict:
    user = load_user(user_id)
    return {"body": format_user(user)}


def load_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}


def format_user(user: dict) -> str:
    return f"{user['id']}: {user['name']}"
```
