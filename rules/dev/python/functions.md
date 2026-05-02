# Python: Functions and Data Structures

How functions are defined: signatures, call site layout, structure rules, and type annotations.

---

## Signatures

For two or more parameters, use `*,` to enforce keyword-only arguments:

- Private functions: `*,` always at the first position (all keyword-only)
- Public functions: may place `*,` after a single leading subject parameter whose identity is already implied by the function name, allowing that subject to be passed positionally

Every parameter goes on its own line with a trailing comma, even for single-parameter functions:

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

## Type Annotations

| Rule | |
|---|---|
| Public functions | fully annotated, parameters and return types |
| Union types | `NDArray[Any] \| list[float]`, `str \| Path`, `float \| None` |
| Private functions | type hints yes, docstrings optional |
| Complex types | use `TypeAlias` |

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

## Call Sites

Pass each argument explicitly by keyword name. Positional-only arguments (e.g. `str.split(",", 1)`) are exempt and may stay inline.

**Single-argument calls** stay on one line:

```python
result = compute_magnitude(vector)
```

**Multi-argument calls** go one argument per line with a trailing comma:

```python
result = compute_something(
    param_a=value_a,
    param_b=value_b,
)
```

**Nested calls** where the outer has one argument and the inner has two or more: expand both:

```python
result = outer_fn(
    inner_fn(
        param_a=value_a,
        param_b=value_b,
    ),
)
```

> **Note:** a short call that fits on one line stays on one line. Break it manually to expand it; once broken, keep it multi-line.
