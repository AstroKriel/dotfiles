# Python: File Layout

The `## { ... }` wrappers delimit file content. Empty files (e.g. `__init__.py` files that only serve as package markers) need no wrapper.

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

class TestFoo_Bar(unittest.TestCase):
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
