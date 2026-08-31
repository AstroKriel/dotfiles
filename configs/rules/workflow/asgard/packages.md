# Asgard: Package Development

Workflow conventions for developing Asgard Python packages.

---

## Git Worktrees

Use git worktrees to develop features without exposing half-finished code to downstream consumers.

Base-clone-on-default, one-worktree-per-branch, location, naming, and pull-before-forking follow [`workflow/git/worktrees.md`](../git/worktrees.md): in Asgard the default branch is `main` (what downstream consumers in `mimir/` resolve to), so the base clone stays on it and worktrees live under `submodules/<package>-worktrees/<branch-slug>`. The rules below add per-worktree environment specifics for Asgard.

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

The main checkout environment is used for forking new feature branches and admin operations; it is never the local link-target downstream consumers resolve to, see [Linking Editable Libraries](#linking-editable-libraries) below.

---

## Linking Editable Libraries

Personal libraries are referenced by a pinned git commit once mature, see [`<rules>/code/asgard.md`](../../code/asgard.md). For active cross-repo development, override the pin locally inside a worktree, but never in the base clone (see [`<rules>/workflow/git/worktrees.md`](../git/worktrees.md)), and never commit the override.

### Opening a `local/main` Worktree

Each package keeps a dedicated worktree that sits at the tip of `<default-branch>` and never takes on any commits directly. Its branch, position relative to the base clone, and lifecycle are:

| Rule | Detail |
|---|---|
| Branch | `local/<default-branch>` |
| Position | `submodules/<package>-worktrees/local-<default-branch>`, alongside feature worktrees |
| Update | fast-forward merge changes in via: `git fetch && git merge --ff-only origin/<default-branch>` |

> **Note:** this worktree should be treated as a pure mirror; no local changes should be made beyond what `<default-branch>` already has, with the only exception its own `[tool.uv.sources]`/`uv.lock` being locally overridden as described below.

### Overriding the Pinned Library

```bash
git update-index --skip-worktree pyproject.toml uv.lock
```

Point `[tool.uv.sources]` at the `local/<default-branch>` worktree for the package, or a feature worktree to test unmerged work:

```toml
[tool.uv.sources]
<package-name> = { path = "../../sindri/submodules/<package>-worktrees/local-<default-branch>", editable = true }
```

Then update the dependency tree:

```bash
uv lock
uv sync
```

`git status` will not track any changes to the ignored files. This is reversed with:

```bash
git update-index --no-skip-worktree pyproject.toml uv.lock
git checkout -- pyproject.toml uv.lock
```

> **Note:** pulling or merging an incoming change to an ignored file is refused, not silently applied.
