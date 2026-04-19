# Python Coding Conventions

These rules define how Python code is written across all personal projects. They apply to any AI assistant helping draft, review, or refactor Python code.

---

## Project Setup

### Package Manager

uv is used for all Python package and project management.

### Personal Libraries

Personal libraries live under `Asgard/sindri/submodules/`. jormi is the primary shared utility library, providing `check_*`, `ensure_*`, type helpers, field utilities, and more. Before writing any new validation, type-checking, or utility logic, check jormi first. New projects should depend on jormi and reuse what it offers rather than reimplementing it.

During active development, personal libraries are referenced as editable installs in `pyproject.toml`:

```toml
[tool.uv.sources]
jormi = { path = "../submodules/jormi", editable = true }
```

Once the project has matured and the dependency on a personal library has stabilised, switch to a pinned git commit version:

```toml
[tool.uv.sources]
jormi = { git = "https://github.com/AstroKriel/jormi", rev = "abc1234" }
```

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

Use basedpyright for type checking (not mypy, not pyright). Include all relevant source and test directories. Suppressed rules must have an inline comment explaining why:

```toml
[tool.pyright]
include = ["src", "utests", "vtests"]
extraPaths = ["src"]
reportMissingImports = true
reportMissingTypeStubs = false        # suppress missing stub warnings for third-party packages
reportExplicitAny = "none"            # numpy/scipy use Any extensively
reportUnknownMemberType = "none"      # cascade from untyped dependencies
reportUnknownVariableType = "none"    # cascade from untyped dependencies
reportUnknownArgumentType = "none"    # cascade from untyped dependencies
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

jormi follows this pattern throughout: each module is named for the operation it performs (`check_types.py`, `ensure_type.py`, `load_config.py`), and when a concept expands, it becomes a package whose sub-modules each own one narrow responsibility. Prefer more smaller modules over one large module.

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

Test files use `## { TEST` / `## } TEST` wrappers, following the same section structure.

---

## Imports

| Rule | |
|---|---|
| Order | `## stdlib` -> `## third-party` -> `## local` -> `## personal` |
| `## local` | imports from within the current project |
| `## personal` | imports from personal libraries under sindri (e.g. jormi) |
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

| Rule | |
|---|---|
| Public functions | short prose docstring: one or two sentences, declarative, ends with a period |
| Private functions | no docstring, rely on type hints and inline comments |
| Classes | one-liner describing what the class represents |

### Inline Comments

| Rule | |
|---|---|
| Standalone marker | `##` (double hash); harder to accidentally uncomment than `#` |
| Inline marker | `#` (single hash) when the comment sits to the right of code on the same line |
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
