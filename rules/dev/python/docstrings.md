# Python: Docstrings and Comments

Code should be self-documenting. A comment is an admission that the code alone is not clear enough. Comments exist to capture the why: to recall why a decision was made, not to describe what the code does.

---

## Docstrings

Write docstrings for all public functions, methods, classes, and dataclasses. Docstrings are optional for private functions and methods.

One-liners have the opening and closing `"""` on the same line. Multi-line docstrings open with `"""` and the text immediately on the first line; the closing `"""` sits on its own line:

```python
"""<One-sentence description ending with a period>."""

"""
<Opening sentence.>

<Optional second paragraph for non-obvious behaviour.>
"""
```

Opening sentence: imperative or declarative voice ("Compute X", "Return X"). Sentence case, ends with a period.

Add a second paragraph only when the opening sentence leaves something genuinely unclear: edge case behaviour, what triggers a raise, a non-obvious side effect. 2-4 sentences max. Never restate what the type annotations already say.

Add a `Parameters ---` section when there are four or more parameters and their constraints are not clear from the type hints alone. Only document what the annotation does not already say:

```python
"""
Short purpose sentence.

Parameters
---
- `param_name`:
    What it expects; constraints; what None means if applicable.
"""
```

Add a `Fields ---` section to a dataclass when field names alone do not convey their constraints or expected shape:

```python
"""
<One-sentence description of what the dataclass represents.>

Fields
---
- `<field>`:
    What it holds; valid ranges or invariants; what None means if applicable.

- `<other_field>`:
    Constraint relating it to another field, if any.
"""
```

| Rule | |
|---|---|
| Names and values | backticks: `` `param_name` ``, `` `True` ``, `` `None` `` |
| Inline math | code style: `` `y = a * x^b` `` |
| Types | never repeat in the docstring; the signature already has them |
| Format | never use numpy/sphinx-style `Parameters:\n-----------` blocks |

---

## Comments

| Rule | |
|---|---|
| Standalone marker | `##` (double hash); harder to accidentally uncomment than `#` |
| Inline marker | `#` (single hash) when the comment sits to the right of code on the same line |
| Spacing | two spaces between code and the `#` marker; do not align inline comments across lines; applies to `pyproject.toml` as well |
| Case | lowercase, unless referring to a named thing: a function, class, constant, or variable |
| Length | a few words to one sentence; never a paragraph |
| Purpose | only three reasons to comment: section structure, non-obvious constraints or invariants, and algorithmic decisions where the why is not derivable from the code |
| Formatting | use backticks for parameter names, flag names, config keys, filenames, and literal values: `` `param_name` ``, `` `--dry-run` ``, `` `this-system.toml` ``, `` `True` `` |
| Silence | leave obvious code uncommented: standard NumPy idioms, straightforward validation calls, and self-documenting function names need no explanation |

Mathematical notation is preferred over English prose where appropriate:

```python
numpy.multiply(
    values,
    values,
    out=out,
)  # out = values^2
```
