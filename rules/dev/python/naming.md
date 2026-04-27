# Python: Naming and Imports

How to name things: files, modules, functions, classes, variables, mathematical variables, and constants.

---

## Files and Modules

| Rule | |
|---|---|
| Casing | `snake_case` for all filenames |
| Pattern | verb-noun: `<verb>_<noun>.py` |
| Private modules | leading underscore: `_<verb>_<noun>.py` |
| Packages | named for the concept they expose: `arrays`, `fields`, `plots` |

A function should only use a leading underscore when it is intended to stay internal to its own module. If a function is called from another module, do not prefix it with an underscore, even if it lives in a private module.

### Module Growth

A single module promoted to a package keeps its name. Sub-modules highlight the sub-concept using the same verb-noun convention:

```
<concept>/
    __init__.py
    <verb>_<noun>.py
    <verb>_<noun>.py
    ...
```

When a concept expands, it becomes a package whose sub-modules each own one narrow responsibility. Typically 50-300 lines; a module approaching 400 lines is a signal to split.

---

## Functions

Always use strong, specific verb prefixes. Avoid weak or generic leading words that do not communicate what the function does or returns:

| Prefix | Purpose |
|---|---|
| `compute_*` | mathematical/numerical operations |
| `check_*` | returns `bool`, may raise or warn; one of two function-level actions under the validate concept |
| `ensure_*` | raises on failure, no meaningful return; the other function-level action under the validate concept |
| `load_*` | I/O that returns data |
| `create_*` / `make_*` | object construction |
| `get_*` | query or lookup |
| `resolve_*` | disambiguation between options |
| `extract_*` | pull data from a larger structure |

Private helpers use a leading underscore: `_<verb>_<noun>()`.

---

## Classes

| Rule | |
|---|---|
| Casing | `PascalCase` for all class, enum, and dataclass names |
| Private classes | leading underscore: `_<Name>` |

---

## Variables

| Rule | |
|---|---|
| Casing | `snake_case` exclusively, never camelCase |
| Abbreviations | acceptable when well-known within the domain |
| Descriptive names | use qualified names that read as subscript notation: `<qualifier>_<noun>` |
| Single-letter names | never; names must always indicate what is being worked with |
| Abbreviated names | never; `language` not `lang`, `index` not `idx` |
| Directories | `directory` when only one in scope; `_dir` suffix when multiple: `source_dir`, `target_dir` |
| Comprehension variables | prepend `_` if the name would conflict with an existing name in scope |
| Booleans | `is_*` or `has_*` prefix |
| Receiver variables | name after the noun in the called function: `<noun> = <verb>_<noun>(...)`, not `result` |

---

### Mathematical Variables

When code, comments, and docstrings use mathematical notation, keep naming aligned with Einstein-style conventions.

| Rule | |
|---|---|
| Scalars | lower-case: `<scalar>` |
| Vectors | lower-case with an index: `<vector>_<index>` |
| Tensors | upper-case with indices: `<Tensor>_<index><index>` |
| Code names | preserve the same distinction in variable names where practical |

When a variable name describes an operation applied to a quantity, separate the action from the quantity with an underscore.

| Rule | |
|---|---|
| Prefer | `<action>_<quantity>` |
| Avoid | `<action><quantity>` |

Apply consistently to variable names, comments, docstrings, and user-facing labels; preserve established public labels when they exist.

### Constants

`UPPER_CASE` at module level:

```python
MAX_ITERATIONS: int = 1000
DEFAULT_TOLERANCE: float = 1e-6
```
