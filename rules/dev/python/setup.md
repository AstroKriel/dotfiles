# Python: Project Setup

How to configure a Python project: package manager, `pyproject.toml`, type checker, and pytest.

---

## Package Manager

uv is used for all Python package and project management.

---

## pyproject.toml

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

For personal libraries installed as editable local dependencies, declare them in `[tool.uv.sources]`. Do **not** add `[tool.hatch.metadata] allow-direct-references = true`; that is only needed for direct URL references written inline in the `dependencies` list. `[tool.uv.sources]` is resolved by uv and hatchling never sees the path:

```toml
dependencies = ["<package-name>"]

[tool.uv.sources]
<package-name> = { path = "<relative-path>", editable = true }
```

---

## Type Checking

Use basedpyright (not mypy, not pyright). Include all relevant source and test directories. Suppressed rules must have an inline comment explaining why. The suppression list below is a menu of acceptable suppressions, not a block to copy wholesale; only add suppressions that are needed for the project after first trying to fix the code:

```toml
[tool.pyright]
include = ["src", "utests", "vtests"]
extraPaths = ["src"]

## --- rules to enforce
reportMissingImports = true
reportMissingTypeStubs = false  # third-party packages rarely ship stubs

## --- rules to suppress
## Add only the suppressions that this project actually needs.
reportExplicitAny = "none"  # numpy/scipy code uses Any extensively; unavoidable
reportAny = "none"  # noisy cascade of the above
reportUnknownMemberType = "none"  # cascade from untyped third-party stubs
reportUnknownVariableType = "none"  # cascade from untyped third-party stubs
reportUnknownArgumentType = "none"  # cascade from untyped third-party stubs
reportImplicitStringConcatenation = "none"  # valid style for long error messages
reportImplicitOverride = "none"  # too verbose to require @override on every override
reportUnusedCallResult = "none"  # ensure_*/check_* are called for side effects
reportPrivateUsage = "none"  # tests legitimately access private members
reportUninitializedInstanceVariable = "none"  # false positive: pyright misses variables set in setUp()
enableTypeIgnoreComments = true  # honour "# type: ignore" (basedpyright defaults to false)
reportIgnoreCommentWithoutRule = "none"  # test files use bare "# type: ignore" intentionally
reportUnnecessaryTypeIgnoreComment = "none"  # suppress warnings about stale ignore comments
reportUnnecessaryIsInstance = "none"  # isinstance guards for runtime safety beyond what annotations enforce
reportUnreachable = "none"  # paired with the above: guards after exhaustive isinstance chains appear unreachable to pyright
```

---

## pytest

Configure pytest with the src layout in mind:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["utests"]
```
