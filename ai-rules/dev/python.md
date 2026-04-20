# Python Coding Conventions

These rules define how Python code is written across all personal projects. They apply to any AI assistant helping draft, review, or refactor Python code.

---

## Project Setup

### Package Manager

uv is used for all Python package and project management.

### pyproject.toml

Use hatchling as the build backend:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Metadata fields follow this order:

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "..."
readme = "README.md"
authors = [{ name = "<name>", email = "<email>" }]
requires-python = ">=3.11"
dependencies = [...]
```

Dev dependencies go in a dependency group:

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.2",
]
```

For personal libraries installed as editable local dependencies, declare them in `[tool.uv.sources]`. Do **not** add `[tool.hatch.metadata] allow-direct-references = true` — that is only needed for direct URL references written inline in the `dependencies` list; `[tool.uv.sources]` is resolved by uv and hatchling never sees the path:

```toml
dependencies = ["<package-name>"]

[tool.uv.sources]
<package-name> = { path = "<relative-path>", editable = true }
```

Use basedpyright for type checking (not mypy, not pyright). Include all relevant source and test directories. Suppressed rules must have an inline comment explaining why:

```toml
[tool.pyright]
include = ["src", "utests", "vtests"]
extraPaths = ["src"]

## --- rules to enforce
reportMissingImports = true
reportMissingTypeStubs = false  # third-party packages rarely ship stubs

## --- rules to suppress
reportExplicitAny = "none"  # numpy/scipy code uses Any extensively; unavoidable
reportAny = "none"  # noisy cascade of the above
reportUnknownMemberType = "none"  # cascade from untyped third-party stubs
reportUnknownVariableType = "none"  # cascade from untyped third-party stubs
reportUnknownArgumentType = "none"  # cascade from untyped third-party stubs
reportImplicitStringConcatenation = "none"  # valid style for long error messages
reportImplicitOverride = "none"  # too verbose to require @override on every override
reportUnusedCallResult = "none"  # ensure_*/check_* are called for side effects
reportPrivateUsage = "none"  # tests legitimately access private members
reportUninitializedInstanceVariable = "none"  # false positive: pyright misses variables set in setUp()
enableTypeIgnoreComments = true  # honour "# type: ignore" (basedpyright defaults to false)
reportIgnoreCommentWithoutRule = "none"  # test files use bare "# type: ignore" intentionally
reportUnnecessaryTypeIgnoreComment = "none"  # suppress warnings about stale ignore comments
```

Configure pytest with the src layout in mind:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["utests"]
```

---

## File & Module Naming

| Rule | |
|---|---|
| Casing | `snake_case` for all filenames |
| Pattern | verb-noun: `compute_array_stats.py`, `load_dataset.py`, `check_arrays.py`, `manage_log.py` |
| Private modules | leading underscore: `_config_types.py`, `_data_operators.py` |
| Packages | `ww_<concept>` prefix; `ww_` means "working with" and marks the public entry point for a concept: `ww_arrays`, `ww_fields`, `ww_plots` |

### Module Growth

A single module promoted to a package keeps its name. Sub-modules highlight the sub-concept using the same verb-noun convention:

```
ww_arrays/
    __init__.py
    compute_stats.py
    load_datasets.py
    check_shapes.py
```

Each module is named for the operation it performs (`parse_config.py`, `validate_schema.py`, `load_dataset.py`), and when a concept expands, it becomes a package whose sub-modules each own one narrow responsibility. Prefer more smaller modules over one large module.

---

## File Layout

Modules follow this structure:

```python
## { MODULE

##
## === DEPENDENCIES
##

## stdlib
...

## third-party
...

## local
...

##
## === TYPE ALIASES
##

...

##
## === SECTION NAME
##

...

## } MODULE
```

Scripts follow this structure:

```python
## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
...

## third-party
...

## local
...

##
## === SECTION NAME
##

...

##
## === PROGRAM MAIN
##

def main() -> None:
    ...

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
```

Unit test files use `## { U-TEST` / `## } U-TEST` wrappers with a `## === TEST SUITE` section instead of `## === PROGRAM MAIN`, and `unittest.main()` as the entry point:

```python
## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
import unittest

## local
...

##
## === TEST SUITE
##

class TestFoo_Bar(unittest.TestCase):
    ...

##
## === ENTRY POINT
##

if __name__ == "__main__":
    unittest.main()

## } U-TEST
```

Validation test files follow the script structure exactly, using `## { V-TEST` / `## } V-TEST` wrappers and a descriptive section header in place of `## === PROGRAM MAIN`:

```python
## { V-TEST

##
## === DEPENDENCIES
##

...

##
## === CONVERGENCE TEST: foo bar
##

def main() -> None:
    ...

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } V-TEST
```

---

## Imports

| Rule | |
|---|---|
| Order | `## stdlib` -> `## third-party` -> `## personal` -> `## local` |
| `## personal` | your own separately-packaged libraries, installed as dependencies |
| `## local` | imports from within the current project |
| Per line | one import per line |
| Aliases | never `import numpy as np` or `import matplotlib.pyplot as plt`, use full names or descriptive aliases: `import numpy`, `import matplotlib.pyplot as mpl_plot`, `from matplotlib.axes import Axes as mpl_Axes` |
| Long imports | use parentheses with trailing commas |

---

## Naming Conventions

### Functions

Use strong verb prefixes, always. Never `calc_`, `process_`, or generic names:

| Prefix | Purpose |
|---|---|
| `compute_*` | mathematical/numerical operations |
| `check_*` | returns `bool`, may raise or warn |
| `ensure_*` | raises on failure (assertion-style) |
| `load_*` | I/O that returns data |
| `create_*` / `make_*` | object construction |
| `get_*` | query or lookup |
| `resolve_*` | disambiguation between options |
| `extract_*` | pull data from a larger structure |
| `validate_*` | raise on invalid state (private use) |

Private helpers use a leading underscore: `_get_bin_edges()`, `_validate_inputs()`, `_extract_column()`.

### Classes

Private classes use a leading underscore: `_Colours`, `_MessageStyle`. These serve as implementation details supporting public classes and are not re-exported.

Enums that are used as strings inherit from both `str` and `Enum`. Enums that are pure value holders inherit from `Enum` only:

```python
class SortOrder(str, Enum): ...   # used as strings
class MessageType(Enum): ...      # pure value holder
```

Enum members may hold dataclass instances as values to carry rich metadata per member:

```python
class MessageType(Enum):
    TASK = _MessageStyle(
        "Task",
        Symbols.RIGHT_ARROW.value,
        _Colours.WHITE.value,
    )
```

### Variables

| Rule | |
|---|---|
| Casing | `snake_case` exclusively, never camelCase |
| Abbreviations | acceptable when well-known within the domain: `ndim`, `cmap`, `num_rows`, `col_index` |
| Descriptive names | use subscript-style: `num_cells_x`, `bin_centers`, `axis_to_slice`, `field_key` |
| Single-letter names | never, names must always indicate what is being worked with |
| Abbreviated names | never, `language` not `lang`, `index` not `idx` |
| Directories | `directory` when only one in scope; `_dir` suffix when multiple: `source_dir`, `target_dir` |
| Comprehension variables | prepend `_` if the name would conflict with an existing name in scope: `_rules_file` |
| Booleans | `is_*` or `has_*` prefix: `is_periodic`, `has_zeros`, `is_open` |

### Constants

`UPPER_CASE` at module level.

---

## Type Annotations

| Rule | |
|---|---|
| Public functions | fully annotated, parameters and return types |
| Union types | `NDArray[Any] \| list[float]`, `str \| Path`, `float \| None` |
| Private functions | type hints yes, docstrings no |
| Complex types | use `TypeAlias`, defined in a dedicated `## === TYPE ALIASES` section |

---

## Function Decomposition

| Rule | |
|---|---|
| Signatures | every parameter on its own line with a trailing comma, even for single-parameter functions; keyword-only arguments enforced with `*` for any function with more than one parameter |
| Call sites | every argument on its own line with a trailing comma, even for single-argument calls |
| Size | typically 20-80 lines, single-responsibility |
| Validation | always separated into `ensure_*` / `check_*` / `_validate_*` helpers, called before any logic |
| Helpers | private (`_` prefix), each doing exactly one sub-task |
| Structure | public functions read as a recipe: validate -> sub-task 1 -> sub-task 2 -> return |

```python
def compute_p_norm(
    *,
    array_a: NDArray[Any],
    array_b: NDArray[Any],
    p_norm: float = 2,
    normalise_by_length: bool = False,
) -> float:

result = compute_p_norm(
    array_a=field_a,
    array_b=field_b,
    p_norm=2,
)
```

---

## Data Structures

| Rule | |
|---|---|
| Containers | prefer `@dataclass(frozen=True)`, immutability by default |
| Derived attributes | use `@cached_property` |
| Alternative constructors | `@classmethod` methods named `from_*` |
| Resource lifecycle | use context managers (`__enter__` / `__exit__`) |

Method ordering within dataclasses:

1. `__post_init__` (validation on construction)
2. Private helper methods (`_` prefix)
3. `@property` methods
4. `@cached_property` methods
5. Regular instance methods
6. `@classmethod` methods

---

## Testing

### Unit Tests (utests)

Unit tests live under `utests/`, mirroring the source structure. Run via pytest.

Test files are named `test_<module_name>.py`. Tests are organised into focused `unittest.TestCase` classes named after what they test:

```python
class TestDataLoader_Construction(unittest.TestCase):

    def test_valid_construction_via_from_dict(
        self,
    ): ...

    def test_frozen_immutability(
        self,
    ): ...

class TestDataLoader_Properties(unittest.TestCase):

    def test_label_is_stored(
        self,
    ): ...

    def test_optional_field_accepts_none(
        self,
    ): ...
```

Private helper functions for building test fixtures use a leading underscore: `_make_config()`, `_make_dataset()`.

Use `assertAlmostEqual()` for floating-point comparisons and `assertRaises()` for error cases:

```python
def test_invalid_input_raises(
    self,
):
    with self.assertRaises(
        TypeError,
    ):
        validate_inputs.ensure_type(
            value=42,
            expected_type=str,
        )
```

### Validation Tests (vtests)

Validation tests live under `vtests/`, mirroring the source structure. Use them when a unit test is not practical: for example, testing numerical convergence, decomposition accuracy, or integrated behaviour across modules.

Each vtest is a standalone script with a `main()` function, discovered and run via `vtests/run_all.py`. Where possible, save visual output (plots, diagrams) alongside the test to allow human inspection of results:

```python
def main() -> None:
    ## run validation
    ...
    ## save visual output
    ...
```

---

## Docstrings & Comments

Code should be self-documenting. A comment is an admission that the code alone is not clear enough. Comments are written for yourself: to recall why a decision was made, not to describe what the code does.

### Docstrings

**When to write:**

| Scope | Rule |
|---|---|
| Public functions and methods | always |
| Private functions and methods | never — rely on type hints and inline comments |
| Classes and dataclasses | always — one sentence describing what the class represents |

**Format:**

One-liners have the opening and closing `"""` on the same line. Multi-line docstrings open with `"""` and the text immediately on the first line; the closing `"""` sits on its own line with no trailing blank line before it:

```python
"""Compute the root-mean-square of a NumPy array."""

"""
Compute the y-intercept b for the line y = slope * x + b
passing through a reference point (x_ref, y_ref).
"""
```

**Opening sentence:**

Always present. Use imperative or declarative voice: *"Compute X"*, *"Return X"*, *"Ensure X raises if..."*. Must fit on one line. Sentence case, ends with a period. If the function name already communicates the intent fully, keep the docstring as short as possible.

**Second paragraph:**

Add only when the opening sentence leaves something genuinely unclear — edge case behaviour, what triggers a raise, a non-obvious side effect, or an important constraint. 2–4 sentences max. Never use it to restate what the type annotations already say.

**Parameters section:**

Add when there are four or more parameters *and* their constraints or relationships are not clear from the type hints alone. Use the `Fields ---` style below. Only document what the type annotation does not already say — valid ranges, what `None` means, dependencies between parameters:

```python
"""
Short purpose sentence.

Parameters
---
- `param_name`:
    What it expects; constraints; what None means if applicable.

- `other_param`:
    Only used when `param_name` is not None.
"""
```

**Dataclass fields:**

Add a `Fields ---` section when field names alone do not convey their constraints or expected shape:

```python
"""
Estimated 1D probability density function from binned data.

Fields
---
- `bin_centers`:
    1D array of bin center positions; must be finite.

- `densities`:
    1D array of probability densities; must be finite, same length as
    `bin_centers`, and normalised so the integral equals 1.
"""
```

**Style:**

| Rule | |
|---|---|
| Names and values | backticks: `` `param_name` ``, `` `True` ``, `` `None` `` |
| Inline math | code style: `` `y = A * x^b` `` |
| Types | never repeat in the docstring — the signature already has them |
| Format | never use numpy/sphinx-style `Parameters:\n-----------` blocks |

### Comments

| Rule | |
|---|---|
| Standalone marker | `##` (double hash); harder to accidentally uncomment than `#` |
| Inline marker | `#` (single hash) when the comment sits to the right of code on the same line |
| Spacing | two spaces between code and the `#` marker; do not align inline comments across lines |
| Case | lowercase, unless referring to a named thing: a function, class, constant, or variable |
| Length | a few words to one sentence; never a paragraph |
| Purpose | only three reasons to comment: section structure, non-obvious constraints or invariants, and algorithmic decisions where the why is not derivable from the code |
| Silence | leave obvious code uncommented: standard NumPy idioms, straightforward validation calls, and self-documenting function names need no explanation |

### Section Markers

Section markers always open and close with an empty `##`. Additional detail lines may follow the heading:

```python
##
## === SECTION NAME
##

##
## === SECTION NAME
## optional detail line.
## can span multiple lines if needed.
##
```

Subsection markers use a single line:

```python
## --- subsection name
```

Mathematical notation is preferred over English prose where appropriate:

```python
numpy.multiply(
    values,
    values,
    out=out,
)  # out = values^2
```

---

## Error Handling

| Rule | |
|---|---|
| Exception types | use builtins: `ValueError`, `TypeError`, `KeyError`, `RuntimeError`, `FileNotFoundError` |
| Messages | always include the parameter name; describe what was wrong and what was expected |
| Formatting | use backticks for variable/parameter names: `` f"`{param_name}` must be one of ..." `` |
| Soft errors | functions that check conditions may accept `raise_error: bool = True`, raise when `True`, log/warn when `False` |
