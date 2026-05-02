# Python: Repo Maintenance

Checks to run when maintaining a Python repo.

---

## When to Run Checks

| Change | Checks |
|---|---|
| Python setup code | Type check and compile check |
| Python package metadata | Type check and compile check |
| Markdown-only changes | No Python checks required |
| Config-only changes | Run project-specific validation if available |

---

## Standard Checks

Run the type checker configured by the project:

```bash
uv run basedpyright
```

Run a compile check over the Python files that make up the repo tooling:

```bash
uv run python -m py_compile <python-file> <package-dir>/*.py
```

---

## Purpose

| Check | Catches |
|---|---|
| `uv run basedpyright` | Type errors, missing imports, renamed fields, wrong call signatures |
| `uv run python -m py_compile ...` | Syntax errors and compile-time Python errors |

These checks are defensive. They catch breakage before another setup run, clean checkout, or fresh machine depends on the repo tooling.
