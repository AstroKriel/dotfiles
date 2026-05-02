# Python: File Layout

How a file is structured internally: wrappers, section markers, imports, and type aliases.

The `## { ... }` wrappers delimit file content. Empty files (e.g. `__init__.py` files that only serve as package markers) need no wrapper.

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
| Module imports | import the module, not individual functions: `from <package>.<module> import <module>` then `<module>.<function>(...)` |
| Long imports | use parentheses with trailing commas when there are three or more names being imported |
| Re-exports | use `from <module> import <name> as <name>` (self-alias) when a module re-exports a symbol for callers; `from <module> import <name>` alone is not considered a re-export by pyright and will produce an error at the call site |

Two exceptions to the module imports rule:

- **Third-party libraries** where a descriptive prefix alias preserves the namespace at the call site. Use `mpl_` for matplotlib, `scipy_` for scipy, `rich_` for rich: `from matplotlib.axes import Axes as mpl_Axes`, `from rich.console import Console as rich_Console`.
- **Universally idiomatic stdlib imports** that are always imported by name: `from pathlib import Path`, `from typing import Any`, `from dataclasses import dataclass`, `from enum import Enum`.

---

## Section Markers

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

---

## Modules

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

---

## Package Init Files

`__init__.py` files that re-export symbols from sub-modules use no wrapper. Use the self-alias pattern so pyright and ruff recognise the imports as explicit re-exports:

```python
from .<module_a> import <name_a> as <name_a>
from .<module_a> import <name_b> as <name_b>
from .<module_b> import <name_c> as <name_c>
```

---

## Type Aliases

Defined in a dedicated `## === TYPE ALIASES` section, before any functions:

```python
##
## === TYPE ALIASES
##

<Name>: TypeAlias = <Type>
```

---

## Scripts

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

---

## Unit Test Files

Use `## { U-TEST` / `## } U-TEST` wrappers with a `## === TEST SUITE` section and `unittest.main()` as the entry point:

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

class Test<Concept>_<Aspect>(unittest.TestCase):
    ...

##
## === ENTRY POINT
##

if __name__ == "__main__":
    unittest.main()

## } U-TEST
```

---

## Validation Test Files

Follow the script structure exactly, using `## { V-TEST` / `## } V-TEST` wrappers and a descriptive section header in place of `## === PROGRAM MAIN`:

```python
## { V-TEST

##
## === DEPENDENCIES
##

...

##
## === CONVERGENCE TEST: <description>
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
