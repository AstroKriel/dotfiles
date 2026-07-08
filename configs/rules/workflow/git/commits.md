# Git: Commits

Conventions for git commit messages: format, actions, scope, granularity, and presentation.

## Format

```
action(scope): details.
```

One line only. No extended description below the subject.

---

## Actions

Use these actions as the default vocabulary. Other verbs are permitted when none of the standard ones fit precisely, as long as the verb is specific and imperative.

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
| `extend` | adding capability to existing functionality |

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

## Granularity

- One logical change per commit.
- Split when changes are independently revertable and target different scopes.
- Keep together when changes are interdependent or incomplete in isolation.

---

## Details

| Rule | Detail |
|---|---|
| Specificity | name what specifically changed, never vague summaries like `update text`, `fix things`, `mend` |
| Case | lowercase throughout |
| Separator | use `;` to separate multiple related changes within one commit |
| Ending | end with a period |
| Length | total length under 100 characters |
| Characters | ASCII only; no special characters |

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

---

## Presenting Commits

| Rule | Detail |
|---|---|
| Format | one shell block per commit containing both `git add` and `git commit` |
| Navigation | always use `cd` to enter the repo; never use `git -C` |

Single repository:

```bash
cd <repo>
git add <path/to/file.py>
git commit -m "<type>(<file.py>): <description>."
```

Multiple repositories:

```bash
cd <repo-a>
git add <path/to/file.py>
git commit -m "<type>(<file.py>): <description>."
```

```bash
cd <repo-b>
git add <path/to/other_file.py>
git commit -m "<type>(<other_file.py>): <description>."
```

---

## Git Helpers

Use the `git_helpers` CLI (`<git-helpers>`) for git operations where a command exists. Fall back to raw `git` only when no equivalent command exists. Full reference: `<git-helpers>/README.md`.
