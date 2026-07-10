# Git: Commits

Conventions for git commit messages: format, actions, scopes, granularity, and presentation.

## Format

Commits are a single line only:

```
<action>-<scope>(<identifier>): <description>.
```

Every commit combines one <action> with one <scope>, joined by a hyphen. The identifier in parentheses is the literal name the scope points to: a function/class name for `fn`, a filename for `file`, a folder name for `folder`, a theme name for `theme`. Omit the parentheses entirely for `repo` level changes, since there is nothing to name.

---

## Actions

Use these actions as the default vocabulary. Other verbs are permitted when none of the standard ones fit precisely, as long as the verb is specific and imperative.

| Action | When |
|---|---|
| `del` | deleting something |
| `add` | creating something new |
| `fix` | bug fix |
| `revert` | undoing or rolling back a previous change on this branch; restoring prior behaviour that was intentionally changed away from |
| `update` | changes to existing functionality |
| `refactor` | restructuring without behaviour change |
| `rename` | renaming something |

---

## Scopes

Scope answers **at what granularity** the change happened. Every action pairs with one of these:

| Scope | What it names |
|---|---|
| `param` | a single parameter, argument, or variable |
| `fn` | a function or class |
| `file` | a whole file |
| `folder` | a whole folder/module |
| `repo` | the whole repository |
| `theme` | a shared theme spanning many files (e.g. linting, type annotations) |

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
del-param(<function>): remove unused <param>.
add-repo: <description of initial repo structure>.
fix-fn(<function>): accept <type> for <param>; accept None for <param>.
revert-theme(<theme>): drop <feature> that shipped only as a diagnostic.
update-file(<file>.py): <description of a broad change within the file>.
refactor-folder(<folder>/): <description of reorganisation across the folder>.
rename-file(<file>.py): rename to <new_file>.py.
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
git commit -m "<action>-<scope>(<file.py>): <description>."
```

Multiple repositories:

```bash
cd <repo-a>
git add <path/to/file.py>
git commit -m "<action>-<scope>(<file.py>): <description>."
```

```bash
cd <repo-b>
git add <path/to/other_file.py>
git commit -m "<action>-<scope>(<other_file.py>): <description>."
```

---

## Git Helpers

Use the `git_helpers` CLI (`<git-helpers>`) for git operations where a command exists. Fall back to raw `git` only when no equivalent command exists. Full reference: `<git-helpers>/README.md`.
