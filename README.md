# pystepdowner

A tool to enforce the **Stepdown Rule** (from Uncle Bob's *Clean Code*) in your Python files.

The Stepdown Rule states that code should be readable from top to bottom. Every function should be followed by those at the next level of abstraction so that we can read the program, descending one level of abstraction at a time as we read down the list of functions.

`pystepdowner` analyzes your Python files and rearranges functions and methods to adhere to this rule, prioritizing source-code call order and correctly handling complex dependency graphs.

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

`pystepdowner` transforms bottom-up code (where helpers are defined before they are used) into top-down code (where the highest-level, most important logic comes first).

**Before (Bottom-Up Architecture):**
```python
# --- Persistence Layer ---
def _execute_query(query: str, params: dict) -> list[dict]:
    return [{"id": 1, "name": "Alice", "role": "admin"}]

def fetch_user_record(user_id: int) -> dict:
    return _execute_query("SELECT * FROM users WHERE id = :id", {"id": user_id})

def fetch_user_permissions(user_id: int) -> list[str]:
    records = _execute_query("SELECT perm FROM user_perms WHERE user_id = :id", {"id": user_id})
    return [r["perm"] for r in records]

# --- Mapping Layer ---
def map_role(role_str: str) -> str:
    return role_str.upper()

def map_permissions(perms: list[str]) -> list[str]:
    return [p.strip() for p in perms]

def build_user_model(record: dict) -> dict:
    return {"id": record["id"], "name": record["name"], "role": map_role(record["role"])}

def build_user_context(user_model: dict, perms: list[str]) -> dict:
    return {"user": user_model, "permissions": map_permissions(perms)}

def map_to_domain(record: dict, perms: list[str]) -> dict:
    user_model = build_user_model(record)
    return build_user_context(user_model, perms)

# --- Service Layer ---
def validate_user_access(domain_user: dict) -> bool:
    return domain_user["user"]["role"] == "ADMIN"

def enrich_user_data(domain_user: dict) -> dict:
    domain_user["status"] = "active"
    return domain_user

def get_user_profile(user_id: int) -> dict:
    record = fetch_user_record(user_id)
    perms = fetch_user_permissions(user_id)
    domain_user = map_to_domain(record, perms)
    if not validate_user_access(domain_user):
        raise ValueError("Access Denied")
    return enrich_user_data(domain_user)

# --- Controller Layer ---
def format_response(profile: dict) -> dict:
    return {"status": 200, "data": profile}

def user_controller(user_id: int) -> dict:
    profile = get_user_profile(user_id)
    return format_response(profile)
```

**After running `pystepdowner rw -i my_script.py`:**
```python
def user_controller(user_id: int) -> dict:
    profile = get_user_profile(user_id)
    return format_response(profile)


def get_user_profile(user_id: int) -> dict:
    record = fetch_user_record(user_id)
    perms = fetch_user_permissions(user_id)
    domain_user = map_to_domain(record, perms)
    if not validate_user_access(domain_user):
        raise ValueError("Access Denied")
    return enrich_user_data(domain_user)


def fetch_user_record(user_id: int) -> dict:
    return _execute_query("SELECT * FROM users WHERE id = :id", {"id": user_id})


def fetch_user_permissions(user_id: int) -> list[str]:
    records = _execute_query("SELECT perm FROM user_perms WHERE user_id = :id", {"id": user_id})
    return [r["perm"] for r in records]


# --- Persistence Layer ---
def _execute_query(query: str, params: dict) -> list[dict]:
    return [{"id": 1, "name": "Alice", "role": "admin"}]


def map_to_domain(record: dict, perms: list[str]) -> dict:
    user_model = build_user_model(record)
    return build_user_context(user_model, perms)


def build_user_model(record: dict) -> dict:
    return {"id": record["id"], "name": record["name"], "role": map_role(record["role"])}


# --- Mapping Layer ---
def map_role(role_str: str) -> str:
    return role_str.upper()


def build_user_context(user_model: dict, perms: list[str]) -> dict:
    return {"user": user_model, "permissions": map_permissions(perms)}


def map_permissions(perms: list[str]) -> list[str]:
    return [p.strip() for p in perms]


# --- Service Layer ---
def validate_user_access(domain_user: dict) -> bool:
    return domain_user["user"]["role"] == "ADMIN"


def enrich_user_data(domain_user: dict) -> dict:
    domain_user["status"] = "active"
    return domain_user


# --- Controller Layer ---
def format_response(profile: dict) -> dict:
    return {"status": 200, "data": profile}
```

## Features

- **Topological Sorting**: Correctly sequences nested function calls and handles mutual recursion.
- **Class Methods**: Seamlessly reorders methods within a class definition.
- **Automatic Annotations**: Automatically inserts `from __future__ import annotations` if an annotation dependency is moved below its definition to avoid `NameError`.
- **Comment Preservation**: Retains module-level and function-level comments in their correct logical blocks.
