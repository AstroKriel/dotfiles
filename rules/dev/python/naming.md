# Python: Naming and Imports

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

## Imports

| Rule | |
|---|---|
| Order | `## stdlib` -> `## third-party` -> `## personal` -> `## local` |
| `## personal` | separately-packaged libraries installed as dependencies |
| `## local` | imports from within the current project |
| Per line | one import per line |
| Within groups | plain `import ...` lines first, then `from ... import ...` lines |
| Sort order | alphabetise imports within each `import ...` and `from ... import ...` block |
| Spacing | separate `import ...` and `from ... import ...` blocks with one blank line when both appear in the same group |
| Aliases | never `import numpy as np` or `import matplotlib.pyplot as plt`; use full names or descriptive aliases: `import numpy`, `import matplotlib.pyplot as mpl_plot`, `from matplotlib.axes import Axes as mpl_Axes` |
| Module imports | import the module, not individual functions: `from <package>.<module> import <module>` then `<module>.<function>(...)`. Exceptions: (1) third-party libraries where a descriptive prefix alias preserves namespace at the call site; use `mpl_` for matplotlib, `scipy_` for scipy, `rich_` for rich (e.g. `from matplotlib.axes import Axes as mpl_Axes`, `from rich.console import Console as rich_Console`); (2) universally idiomatic stdlib imports: `from pathlib import Path`, `from typing import Any`, `from dataclasses import dataclass`, `from enum import Enum` |
| Long imports | use parentheses with trailing commas when there are three or more names being imported |
| Re-exports | use `from <module> import <name> as <name>` (self-alias) when a module re-exports a symbol for callers; `from <module> import <name>` alone is not considered a re-export by pyright and will produce an error at the call site |

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

Private classes use a leading underscore. They serve as implementation details supporting public classes and are not re-exported.

Enums that are used as strings inherit from both `str` and `Enum`. Enums that are pure value holders inherit from `Enum` only:

```python
class <Name>(str, Enum): ...   # used as strings
class <Name>(Enum): ...        # pure value holder
```

Enum members may hold dataclass instances as values to carry rich metadata per member:

```python
class <EnumName>(Enum):
    <MEMBER> = <DataclassType>(
        <arg>,
        <arg>,
        <arg>,
    )
```

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

---

## Mathematical Naming

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

This makes differential and tensor expressions easier to scan in code. Apply consistently to variable names, comments, docstrings, and user-facing labels (unless an established public label should be preserved).

---

## Constants

`UPPER_CASE` at module level.
