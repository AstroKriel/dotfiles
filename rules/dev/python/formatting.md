# Python: Formatting

Formatting rules describe how code should be written. 

---

## Function Signatures

Every parameter goes on its own line with a trailing comma, even for single-parameter functions. The formatter enforces this unconditionally:

```python
def <verb>_<noun>(
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

**Multi-argument calls** go one argument per line with a trailing comma. Positional-only arguments (e.g. `str.split(",", 1)`) are exempt and may stay inline:

```python
result = compute_something(
    param_a=value_a,
    param_b=value_b,
)
```

**Nested calls** where the outer has one argument and the inner has two or more: the formatter auto-expands both:

```python
result = outer_fn(
    inner_fn(
        param_a=value_a,
        param_b=value_b,
    ),
)
```

---

## Type Annotations

| Rule | |
|---|---|
| Public functions | fully annotated, parameters and return types |
| Union types | `NDArray[Any] \| list[float]`, `str \| Path`, `float \| None` |
| Private functions | type hints yes, docstrings optional |
| Complex types | use `TypeAlias` |
