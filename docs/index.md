# pystepdowner

A tool to enforce the **Stepdown Rule** (from Uncle Bob's *Clean Code*) in your Python files.

The Stepdown Rule states that code should be readable from top to bottom. Every function should be followed by those at the next level of abstraction so that we can read the program, descending one level of abstraction at a time as we read down the list of functions.

`pystepdowner` analyzes your Python files and rearranges functions and methods to adhere to this rule, prioritizing source-code call order and correctly handling complex dependency graphs.

## Installation

You can install `pystepdowner` as a global CLI tool using `uv` (recommended):

```bash
--8<-- "docs_src/index/install_uv.sh"
```

Alternatively, you can install it into any Python environment using standard `pip`:

```bash
--8<-- "docs_src/index/install_pip.sh"
```

## Usage

The CLI provides two main commands: `fmt` and `rw`.

### 1. `fmt`: Format and Print to Output
Use the `fmt` command to format a single file and output the result to your terminal. This is useful for previewing changes without modifying the actual file.

```bash
--8<-- "docs_src/index/fmt.sh"
```

### 2. `rw`: Rewrite Files
Use the `rw` command to format and rewrite files. You can rewrite a single file or an entire directory recursively.

#### Rewrite a Single File In-Place
```bash
--8<-- "docs_src/index/rw_in_place.sh"
```

#### Rewrite a Single File and Save to a New Location
```bash
--8<-- "docs_src/index/rw_output.sh"
```

#### Rewrite an Entire Directory In-Place
This will recursively find and format all `.py` files inside the target directory.

```bash
--8<-- "docs_src/index/rw_directory.sh"
```

## Example

`pystepdowner` transforms bottom-up code into top-down code, putting high-level logic before the helpers it calls.

**Before:**
```python
--8<-- "docs_src/index/example_before.py"
```

**After running `pystepdowner rw -i my_script.py`:**
```python
--8<-- "docs_src/index/example_after.py"
```

## Features

- **Topological Sorting**: Correctly sequences nested function calls and handles mutual recursion.
- **Class Methods**: Seamlessly reorders methods within a class definition.
- **Automatic Annotations**: Automatically inserts `from __future__ import annotations` if an annotation dependency is moved below its definition to avoid `NameError`.
- **Comment Preservation**: Retains module-level and function-level comments in their correct logical blocks.
