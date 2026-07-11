# Git: Worktrees

Conventions for git worktree layout, naming, and lifecycle.

## Layout

Keep the default branch checked out on the base clone and never switch it; do every feature branch in its own worktree. Downstream consumers and stable references always point at the base clone, so they see stable code regardless of what feature work is in flight.

Group a codebase's worktrees under a single `<codebase>-worktrees/` directory sibling to the base clone, never as flat `<codebase>-<branch-slug>` siblings. This keeps the parent directory uncluttered and worktrees discoverable in one place.

```
<codebase>/                          base clone, always on the default branch
<codebase>-worktrees/<branch-slug>   one directory per active feature branch
```

| Rule | Detail |
|---|---|
| Base clone on default branch | the base clone stays on the default branch (`main`, `development`, ...); worktrees branch off from there |
| Base clone stays clean | never build, edit, or run experiments directly in the base clone, even for throwaway work with no intent to commit; use a worktree instead, e.g. a `tmp/<name>` branch for non-committal exploration (see [`workflow/git/branches.md`](branches.md)) |
| One worktree per feature branch | create a worktree for each active feature branch; remove it when the branch is merged or shelved |
| Location | worktrees live under `<codebase>-worktrees/`, a sibling of the base clone |
| Naming | name each worktree after its branch with `/` replaced by `-`: branch `<verb>/<name>` becomes `<codebase>-worktrees/<verb>-<name>` |
| Pull before forking | before creating a worktree off a passive tracking branch (e.g. the default branch), pull it so the new branch starts from the latest stable state |

Codebase-specific rules may adjust the parent path (e.g. worktrees inside `submodules/`, or separate local vs HPC roots) or add setup steps (submodule init, per-worktree environments, build trees), but the base-clone-on-default plus `<codebase>-worktrees/<branch-slug>` shape stays fixed.
