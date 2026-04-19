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
| One file, localised change | function or class name: `fn_name`, `ClassName` |
| One file, broad change | filename with extension: `file_name.py` |
| Many files, shared concept | concept name: `linting`, `type annotations`, `imports` |
| Folder rename | folder name with trailing slash: `folder/` |
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

## Presenting Commits

When suggesting commits, always present each one as a copy-pasteable shell block containing both the `git add` and `git commit` commands. If the work spans multiple repositories, prepend a `cd` command to each block.

Single repository:

```bash
git add src/data_loader.py
git commit -m "fix(data_loader.py): handle missing file path by raising FileNotFoundError."
```

Multiple repositories:

```bash
cd ~/Projects/package-a
git add src/package_a/validate_inputs.py
git commit -m "fix(validate_inputs.py): raise TypeError when input type is invalid."
```

```bash
cd ~/Projects/package-b
git add src/package_b/process_data.py
git commit -m "update(process_data.py): use package-a validate_inputs for type checking."
```

---

## Commit Message Examples

These illustrate the message format and wording style only, not the full shell workflow:

```
fix(data_loader.py): handle missing file path by raising FileNotFoundError.
refactor(data_loader.py): expand function signatures to one arg per line.
fix(compute_stats): accept int for bin_count; accept None for label.
apply(linting): fix ruff and pyright warnings across src/.
rename(plots/): align module names with verb-noun convention.
add: initial repo structure.
```
