# Python: Functions and Data Structures

---

## Signatures

For two or more parameters, use `*,` to enforce keyword-only arguments:

- Private functions: `*,` always at the first position (all keyword-only)
- Public functions: may place `*,` after a single leading subject parameter whose identity is already implied by the function name, allowing that subject to be passed positionally

```python
## all keyword-only: when the subject is not implied by the function name
def <verb>_<noun>(
    *,
    <param>: <type>,
    <param>: <type>,
    <param>: <type> = <default>,
) -> <type>:

## subject-first: when the function name already identifies the subject type, making its position unambiguous
def <verb>_<noun>(
    <subject>: <type>,
    *,
    <param>: <type>,
    <param>: <type> = <default>,
) -> <type>:
```

---

## Call Sites

Pass each argument explicitly by keyword name. Positional-only arguments (e.g. `str.split(",", 1)`) are exempt and may stay inline.

---

## Structure

| Rule | |
|---|---|
| Size | typically 20-80 lines, single-responsibility |
| Blank lines | no blank lines inside a function body, except one blank line above and below a nested function definition |
| Validation | always separated into `ensure_*` / `check_*` helpers, called before any logic |
| Helpers | private (`_` prefix), each doing exactly one sub-task |
| Recipe | public functions read as a recipe: validate -> sub-task 1 -> sub-task 2 -> return |

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
