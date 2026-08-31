# Git: Branch Naming

Conventions for naming git branches.

## Format

```
verb/short-description
```

For shared repos (multiple contributors), prepend a username:

```
username/verb/short-description
```

| Rule | Detail |
|---|---|
| Case | lowercase throughout |
| Separators | `/` for namespaces, `-` for words within a namespace |
| Length | max 50 characters |
| Characters | alphanumeric, `-`, and `/` only |
| Purpose | one branch per logical change |
| Verbs | same as [commit actions](commits.md): `add`, `fix`, `refactor`, `update`, `extend`, `del`, etc. |
| Avoid | dates, vague names (`wip`, `temp`, `fix-stuff`), and anything longer than needed |
| `tmp/` requirement | any branch not intended to ever be merged (a throwaway verification build, an A/B comparison, exploratory-only work) must use `tmp/<name>` in place of the verb slot, e.g. `username/tmp/short-description` in a shared repo; a deliberate namespace, not the vague `temp` naming otherwise avoided |
| `local/` requirement | a worktree that exists purely as a stable link-target for other repos' local dependency overrides, never receiving its own commits, uses `local/<default-branch>` in place of the verb slot, e.g. `local/main`; a deliberate namespace like `tmp/`, not a verb; see [`<rules>/workflow/asgard/packages.md`](../asgard/packages.md) for the workflow it supports |
| Lifecycle | delete branches after merging; rebase onto `main` before opening a PR |
