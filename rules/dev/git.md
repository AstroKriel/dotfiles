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
| `apply` | applying external changes (linting, formatting, style) |
| `config` | config file changes |
| `docs` | documentation only |
| `test` | test additions or fixes |

---

## Scope

Scope answers **where** the change is. Granularity depends on how localised the change is:

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
| Characters | ASCII only; no special characters |

---

## Branch Naming

```
verb/short-description
```

For shared repos (multiple contributors), prepend a username:

```
username/verb/short-description
```

| Rule | |
|---|---|
| Case | lowercase throughout |
| Separators | `/` for namespaces, `-` for words within a namespace |
| Length | max 50 characters |
| Characters | alphanumeric, `-`, and `/` only |
| Purpose | one branch per logical change |

Use the same verbs as commits: `add`, `fix`, `refactor`, `update`, `del`, etc.

**Avoid:** dates, vague names (`wip`, `temp`, `fix-stuff`), and anything longer than needed.

**Lifecycle:** delete branches after merging; rebase onto `main` before opening a PR.

---

## Presenting Commits

When suggesting commits, always present each one as a copy-pasteable shell block containing both the `git add` and `git commit` commands. Always use `cd` to navigate into the repo; never use `git -C`.

Single repository:

```bash
cd ~/Projects/<repo>
git add <path/to/file.py>
git commit -m "<type>(<file.py>): <description>."
```

Multiple repositories:

```bash
cd ~/Projects/<repo-a>
git add <path/to/file.py>
git commit -m "<type>(<file.py>): <description>."
```

```bash
cd ~/Projects/<repo-b>
git add <path/to/other_file.py>
git commit -m "<type>(<other_file.py>): <description>."
```

---

## Git Helpers

Use the `git_helpers` CLI (`~/Projects/GitHelpers`) for git operations where a command exists. Fall back to raw `git` only when no equivalent command exists. Full reference: `~/Projects/GitHelpers/README.md`.

---

## Commit Message Examples

These illustrate the message format and wording style only, not the full shell workflow:

```
fix(<script>.py): <description of what was broken and how it is fixed>.
refactor(<module>.py): <description of structural change>.
fix(<function>): accept <type> for <param>; accept None for <param>.
apply(linting): fix ruff and pyright warnings across src/.
rename(<dir>/): <description of naming change>.
add: initial repo structure.
```
