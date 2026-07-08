# Asgard: Package Development

Workflow conventions for developing Asgard Python packages.

---

## Git Worktrees

Use git worktrees to develop features without exposing half-finished code to downstream consumers.

Base-clone-on-default, one-worktree-per-branch, location, naming, and pull-before-forking follow [`workflow/git/worktrees.md`](../git/worktrees.md): asgard's default branch is `main` (what downstream consumers in `mimir/` resolve to), so the base clone stays on it and worktrees live under `submodules/<package>-worktrees/<branch-slug>`. The rules below add asgard's per-worktree environment specifics.

| Rule | Detail |
|---|---|
| Isolated environment | Each worktree has its own `.venv`; create and editable-install on creation. See [Environment](#environment) below. |
| Trial scripts | Short-lived scratch scripts belong inside the feature worktree, not the main checkout. |

Pull first:

```bash
git pull
```

Then create the worktree:

```bash
git worktree add ../<package>-worktrees/<branch-slug> -b <verb>/<name>
cd ../<package>-worktrees/<branch-slug>
```

Remove a worktree when the branch is merged or shelved:

```bash
git worktree remove ../<package>-worktrees/<branch-slug>
```

### Environment

Each worktree has its own `.venv` so scripts and tests run against the feature branch code. `<branch-slug>` is the branch name with `/` replaced by `-` (e.g. `<verb>-<name>`).

```bash
cd ../<package>-worktrees/<branch-slug>
uv venv
uv pip install -e .
```

The main checkout's environment is what downstream consumers (projects in `mimir/`) resolve to; the worktree environment is only active when explicitly activated.
