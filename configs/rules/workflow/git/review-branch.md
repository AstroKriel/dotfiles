# Git: Branch Review

How to review a branch before pushing.

---

## Workflow

1. Get the full list of changed files vs the base branch.

```bash
git_helpers show-commits-on-branch --show-files-changed
```

2. Get a flat list of changed files.

```bash
git_helpers show-diff-committed --name-only
```

3. Review each file in turn.

To review committed changes on a branch:

```bash
git_helpers show-diff-committed --path <file>
```

To review changes before committing them:

```bash
git_helpers show-diff-uncommitted --path <file>
```

To review new files, which have no history to diff against:

```bash
git_helpers show-diff-untracked <file>
```

> **Note:** append `> /tmp/review.diff` to any of the diff-commands above, to review the full set of changes in a file rather than scrolling through the terminal output.

For each file, make sure you understand what changed and why, that no unintended changes are present, and that all callers or dependents of changed code were updated. Move to the next file only once this is clear.

---

## Completeness check

A diff review will only reveal files you already know about, so, if a shared interface changed (e.g., function signature, callable contract, template parameter), grep for all callers before starting the file-by-file review. Confirm every caller was updated.

```bash
grep -r "<changed-symbol>" <src-directory>
```

---

## Before pushing

- Run any pre-commit, format, or lint hooks the repository defines before pushing; resolve what they report.
- The invocation is repository-specific; find it in the repository's own docs or config.
