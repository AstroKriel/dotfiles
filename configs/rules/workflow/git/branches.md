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
| `tmp/` exception | `tmp/<name>` is reserved for throwaway, non-committal work (e.g. a quick verification build); a deliberate namespace, not the vague `temp` naming otherwise avoided |
| Lifecycle | delete branches after merging; rebase onto `main` before opening a PR |
