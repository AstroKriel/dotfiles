# Git Commit Rules

## Format

```
action(scope): details.
```

One line only. No extended description below the subject.

---

## Actions

Use only these actions:

| Action | When |
|---|---|
| `add` | new functionality |
| `fix` | bug fix |
| `refactor` | restructuring without behaviour change |
| `rename` | renaming files, functions, variables |
| `del` | deleting code or files |
| `update` | changes to existing functionality |
| `improve` | quality/clarity improvements |
| `apply` | applying external changes (linting, formatting) |
| `config` | config file changes |
| `docs` | documentation only |
| `test` | test additions or fixes |

---

## Scope

Scope answers *where* the change is. Granularity depends on how localised the change is:

| Situation | Scope |
|---|---|
| One file, localised change | function or class name: `add_colorbar` |
| One file, broad change | filename with extension: `annotate_axis.py` |
| Many files, shared concept | concept name: `linting`, `type annotations`, `imports` |
| Repo-wide | omit scope entirely |

---

## Details

| Rule | |
|---|---|
| Specificity | name what specifically changed, never vague summaries like `update text`, `fix things`, `mend` |
| Case | lowercase throughout |
| Separator | use `;` to separate multiple related changes within one commit |
| Ending | end with a period |
| Length | total length under 100 characters |

---

## Examples

```
fix(annotate_axis.py): broaden color params to accept RGBA tuples.
refactor(annotate_axis.py): expand function signatures to one arg per line.
fix(add_colorbar): broaden label_size to accept int; broaden color params to accept RGBA tuples.
apply(linting): fix ruff and pyright warnings across ww_fields.
rename(ww_plots): align module names with verb-noun convention.
add: initial repo structure.
```
