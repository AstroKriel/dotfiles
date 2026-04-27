# Python: Functions and Data Structures

---

## Type Annotations

| Rule | |
|---|---|
| Public functions | fully annotated, parameters and return types |
| Union types | `NDArray[Any] \| list[float]`, `str \| Path`, `float \| None` |
| Private functions | type hints yes, docstrings optional |
| Complex types | use `TypeAlias`, defined in a dedicated `## === TYPE ALIASES` section |

---

## Function Signatures

Every parameter goes on its own line with a trailing comma, even for single-parameter functions.

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

**Single-argument calls** stay on one line:

```python
result = compute_magnitude(vector)
```

**Multi-argument calls** go one argument per line, keyword-named, with a trailing comma. Positional-only arguments (e.g. `str.split(",", 1)`) are exempt and may stay inline:

```python
result = compute_something(
    param_a=value_a,
    param_b=value_b,
)
```

**Nested calls** where the argument is itself a call expression: expand both the outer and inner call to multi-line:

```python
result = outer_fn(
    inner_fn(
        param_a=value_a,
        param_b=value_b,
    ),
)
```

---

## Function Structure

| Rule | |
|---|---|
| Size | typically 20-80 lines, single-responsibility |
| Blank lines | no blank lines inside a function body, except one blank line above and below a nested function definition |
| Validation | always separated into `ensure_*` / `check_*` helpers, called before any logic |
| Helpers | private (`_` prefix), each doing exactly one sub-task |
| Structure | public functions read as a recipe: validate -> sub-task 1 -> sub-task 2 -> return |

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
