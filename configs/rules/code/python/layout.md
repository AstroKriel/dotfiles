# Python: File Layout

How to lay out a Python file, from wrappers and section markers through imports and type aliases.

---

## Wrappers

Every file begins and ends with a wrapper that identifies its type:

| File type | Wrapper |
|---|---|
| Module | `## { MODULE` / `## } MODULE` |
| Script | `## { SCRIPT` / `## } SCRIPT` |
| Unit test | `## { U-TEST` / `## } U-TEST` |
| Validation test | `## { V-TEST` / `## } V-TEST` |

Empty files (e.g. `__init__.py` package markers) need no wrapper.

---

## Section Markers

Section markers always open and close with an empty `##`. Additional detail lines may follow the heading:

```python
##
## === SECTION NAME
##

...

##
## === SECTION NAME
## optional detail line.
## can span multiple lines if needed.
##
```

Subsection markers use a single line:

```python
## --- SUBSECTION NAME
```

---

## Imports

**Order:**

1. `## stdlib`: standard library
2. `## third-party`: external packages
3. `## personal`: separately-packaged libraries installed as dependencies
4. `## local`: imports from within the current project

**Style:**

| Rule | Detail |
|---|---|
| Per line | one import per line |
| Within groups | `import ...` lines first, then `from ... import ...` lines |
| Sort order | alphabetise within each block |
| Spacing | one blank line between the two blocks when both appear in the same group |
| Aliases | never `import <module> as <abbrev>`; use the full name or a descriptive alias |
| Module imports | import the module, not individual functions: `from <package>.<module> import <module>` then `<module>.<function>(...)` |
| Long imports | use parentheses with trailing commas when there are three or more names |
| Re-exports | use `from <module> import <name> as <name>` (self-alias) so pyright recognises the re-export |

Exceptions to the module imports rule:

| Exception | Detail |
|---|---|
| Third-party with namespace prefix | `from <package>.<module> import <Class> as <prefix>_<Class>`; use `mpl_` for matplotlib, `scipy_` for scipy, `rich_` for rich |
| Universally idiomatic stdlib | `from pathlib import Path`, `from typing import Any`, `from dataclasses import dataclass`, `from enum import Enum` |

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

## File Patterns

### Module

```python
## { MODULE

##
## === DEPENDENCIES
##

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

### Script

```python
## { SCRIPT

##
## === DEPENDENCIES
##

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

### Package Init

`__init__.py` files that re-export symbols use no wrapper. Use the self-alias pattern so pyright and ruff recognise the imports as explicit re-exports:

```python
from .<module_a> import <name_a> as <name_a>
from .<module_a> import <name_b> as <name_b>
from .<module_b> import <name_c> as <name_c>
```

### Unit Test

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

### Validation Test

A validation test is a class, not a `main()` function; see [`testing.md`](testing.md) for the full structure.

```python
## { V-TEST

##
## === DEPENDENCIES
##

...

##
## === <DESCRIPTION> TEST
##

class Test<Concept>:

    def __init__(
        self,
    ):
        ...

    def run(
        self,
    ) -> None:
        ...

##
## === ENTRY POINT
##

if __name__ == "__main__":
    style_plots.set_theme()
    test = Test<Concept>()
    test.run()

## } V-TEST
```
