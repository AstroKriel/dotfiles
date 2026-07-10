# Quokka: Build and Run

Quokka build and run workflow on local and hpc systems.

## Related Orientation

| Location | What |
|---|---|
| `<quokka-checkout>/CLAUDE.md` | Architecture, build commands, code style, GPU safety. Maintained by the repo. |
| `<quokka-checkout>/AGENTS.md` | LLM agent guidance for the Quokka codebase. Maintained by the repo. |
| `<quokka-checkout>/docs/markdown/` | Full user and developer documentation. Key files: `mhd_module.md` (MHD physics and runtime controls), `parameters.md` (all TOML parameters), `running_on_hpc_clusters.md` (cluster-specific build procedures), `contributing.md` (git workflow, PR guidelines, code style). |
| `<project-notes>/codebases/quokka/` | Orientation: what Quokka is, file locations on this machine. |

---

## Build Directories

| Rule | Detail |
|---|---|
| Always start cold | Do not assume a build is still valid when resuming work on a branch. Delete `CMakeCache.txt` and reconfigure from scratch. |
| One config per tree | Never share a build tree between configurations. Name each tree after its configuration, e.g. `build/3d-release`, `build/3d-debug`. |
| No Python | Always pass `-DQUOKKA_PYTHON=OFF`. Do not create a Python environment inside the quokka checkout; all analysis goes through `ww-quokka-sims`. |
| Toolchain | When a host needs a non-default compiler, source `~/.config/quokka/profile.sh` before running CMake. Per-host specifics live in `<project-notes>/hpcs/<host>/`. |
| Pin build tools explicitly | On HPC nodes, always pass `-DCMAKE_MAKE_PROGRAM`, `-DCMAKE_AR`, and `-DCMAKE_RANLIB` explicitly on the cmake command line, **and** `rm -f CMakeCache.txt` before configuring. Command-line `-DCMAKE_*` flags are silently overridden by cached values when `CMakeCache.txt` exists; deleting the cache is the only reliable fix. |

Common configurations:

```bash
cmake -S . -B build/3d-release -G Ninja -DCMAKE_BUILD_TYPE=Release -DAMReX_SPACEDIM=3 -DQUOKKA_PYTHON=OFF
cmake -S . -B build/3d-debug   -G Ninja -DCMAKE_BUILD_TYPE=Debug   -DAMReX_SPACEDIM=3 -DQUOKKA_PYTHON=OFF
cmake -S . -B build/3d-asan    -G Ninja -DCMAKE_BUILD_TYPE=Debug   -DAMReX_SPACEDIM=3 -DQUOKKA_PYTHON=OFF -DENABLE_ASAN=ON
```

On HPC nodes where system modules may be architecture-specific, use portable tool installs instead:

```bash
# Install a portable ninja wheel (manylinux, works on any x86_64 node):
pip install --user ninja          # installs to ~/.local/bin/ninja

# Then configure with explicit tool pins:
rm -f "$BUILD/CMakeCache.txt"
cmake -S "$SRC" -B "$BUILD" -G Ninja \
    -DCMAKE_MAKE_PROGRAM=$HOME/.local/bin/ninja \
    -DCMAKE_AR=/usr/bin/ar \
    -DCMAKE_RANLIB=/usr/bin/ranlib \
    ...
```

> **Note:** module-provided tools are compiled for a specific CPU ISA; using them on a different node type causes silent crashes. See [`workflow/remote-work/hpc.md`](../remote-work/hpc.md) for the general rule.

---

## Git Worktrees

Use git worktrees to work on multiple feature branches in parallel without switching branches or invalidating builds.

Base-clone-on-default, one-worktree-per-branch, location, naming, and pull-before-forking follow [`workflow/git/worktrees.md`](../git/worktrees.md): quokka's default branch is `development`, so the base clone stays on it and worktrees live under `quokka-worktrees/<branch-slug>`. The rules below add quokka's submodule, extern, and build-tree specifics.

| Rule | Detail |
|---|---|
| Initialise submodules on creation | After `git worktree add`, run `git submodule update --init` inside the new worktree before building. The `--init` flag is required on any fresh worktree: submodule registration does not carry over from the main checkout automatically. Subsequent updates (e.g. after pulling a new pin) only need `git submodule update`. |
| Extern drift | Each worktree has its own `extern/` working tree; submodule pins are per-branch. If a feature branch falls behind `development` on submodule pins, fix by merging or rebasing `development` into the feature branch so the pins come back into sync. |
| Build directories | Each worktree has its own build tree. On local, build dirs live inside the worktree (`build/3d-release`, etc.). On HPC, source lives on quota-limited Ceph home; build dirs go on node-local scratch. See Build locations below. |
| Trial run data | Short-lived `sims/` runs belong inside the feature worktree, not the main checkout. |

If the source branch is a passive tracking branch (e.g. `development`), pull before creating the worktree. Skip this for active feature branches where the current state is intentional.

```bash
git pull
```

Then create the worktree:

```bash
git worktree add ../quokka-worktrees/<branch-slug> <branch>
cd ../quokka-worktrees/<branch-slug>
git submodule update --init
```

Remove a worktree when the branch is merged or shelved:

```bash
git worktree remove ../quokka-worktrees/<branch-slug>
```

### Build locations

Worktrees are the same concept on local and HPC; only where the build tree lives differs. `<branch-slug>` is the branch name with `/` replaced by `-` (e.g. `<scope>-add-<name>`).

**Local:** build dirs sit inside the worktree, source and build co-located. Run from inside the worktree directory:

```bash
cmake -S . -B build/3d-release -G Ninja -DCMAKE_BUILD_TYPE=Release -DAMReX_SPACEDIM=3 -DQUOKKA_PYTHON=OFF
cmake -S . -B build/3d-debug   -G Ninja -DCMAKE_BUILD_TYPE=Debug   -DAMReX_SPACEDIM=3 -DQUOKKA_PYTHON=OFF
ninja -C build/3d-release <ProblemName>
```

**HPC:** source worktrees live on quota-limited home; build trees go on node-local scratch. Use explicit `-S`/`-B` to separate them. Toolchain flags vary per host; see host notes and the portable tool install block in Build Directories above:

```bash
SRC=<repos>/quokka-worktrees/<branch-slug>
BUILD=<scratch>/$USER/quokka-worktrees/<branch-slug>/build/<config>
rm -f "$BUILD/CMakeCache.txt"
cmake -S "$SRC" -B "$BUILD" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DAMReX_SPACEDIM=3 \
    -DQUOKKA_PYTHON=OFF \
    # ... plus host-specific toolchain flags
ninja -C "$BUILD" <ProblemName>
```

`<repos>` and `<scratch>` are defined in `<project-notes>/hpcs/<host>/`. The worktree path (`quokka-worktrees/<branch-slug>`) is the same in both cases; only the root path differs.

---

## The `quokka` Script

`scripts/bash/quokka` is a thin wrapper around CMake, Ninja, and CTest.

| Command | What it does |
|---|---|
| `quokka list` | List problem directories under `src/problems/`. |
| `quokka target` | Print the raw CMake target list. |
| `quokka clean` | Remove plotfiles, checkpoints, and output files from `tests/`. |

Typical workflow (after configuring a build tree):

```bash
# Build
ninja -C build/3d-release <ProblemName>

# Run
cd tests && ../build/3d-release/src/problems/<ProblemName>/<ProblemName> ../inputs/<ProblemName>.toml
```

### Prefer raw tools over the wrapper

- Drive `cmake`, `ninja`, and the compiled binary directly rather than through `scripts/bash/quokka` or CTest; the wrapper and harness encode other contributors' tolerances and plumbing.
- Reserve the wrapper for listing problems and bulk test runs.
- Do not go below CMake to hand-invoke the compiler; the build system and its required flags are not optional.

---

## HPC Run Setup

Quokka maps onto the standard project layout from [`workflow/remote-work/hpc.md`](../remote-work/hpc.md):

| Concept | Quokka name | Notes |
|---|---|---|
| `<sim-inputs>` | `<problem>.toml` | TOML input file for the problem |
| `<sim-outputs>` | `snapshots/` | AMReX HDF5 plotfiles |
| `<derived>` | `diagnostics/` | Extracted data from `ww-quokka-sims` |

Checkpoints (restart files, not analysis output) get their own `checkpoints/` folder, separate from `<sim-outputs>`; there is no generic-concept equivalent for this in [`workflow/remote-work/hpc.md`](../remote-work/hpc.md), it is Quokka-specific.

```text
<concept>/<sim-name>/
├── jobs/
│   ├── sim.sh
│   └── extract.sh
├── <problem>.toml
├── logs/
├── snapshots/
├── checkpoints/
└── diagnostics/
```

Point AMReX output to `snapshots/` and `checkpoints/` in the run TOML:

```toml
plotfile_prefix = "snapshots/plt"
checkpoint_prefix = "checkpoints/chk"
```

AMReX profiling output (`ProfData_*`) lands in the working directory; with `--chdir`/`-d` set to the run directory, this goes to the run root rather than `logs/`.

| Script | Purpose |
|---|---|
| `jobs/sim.sh` | Run the Quokka executable with the problem TOML |
| `jobs/extract.sh` | Run `ww-quokka-sims` diagnostics; output goes to `diagnostics/` |

For short-lived trial runs (testing a parameter, trialing a scheme), use `sims/<purpose>/<problem>/` under the worktree rather than a full `<concept>/<sim-name>/` directory. See [`workflow/quokka/testing.md`](testing.md) for the layout convention.

### Run settings

- **Verbose output:** always set `amr.v = 1`. This enables FOFC firing counts, retry events, and other internal solver diagnostics that are silent at the default `amr.v = 0`.
- **Plotfiles:** always set `plottime_interval = <interval>`. Write snapshots at regular intervals so the evolution can be inspected, not just the outcome. A run that crashes with no plotfiles leaves nothing to analyse.
- **Checkpoints:** set `checkpointtime_interval = <interval>` and `checkpoint_prefix = "checkpoints/chk"` for jobs that may run close to the partition's wall-time limit, so the job can be resubmitted with `restartfile = <checkpoint-name>` instead of restarting from scratch. See [`workflow/remote-work/hpc.md`](../remote-work/hpc.md) for the general rule.
- **Pass TOML as a relative path:** always pass the input file as a bare filename (`sim_params.toml`), not an absolute path, and set the working directory to the run directory before invoking the binary (`cd $RUNDIR` in PBS/SLURM scripts; `--chdir` in SLURM). AMReX ParmParse treats any command-line token containing `=` as an inline key=value pair. Absolute paths through directories named with `key=value` segments (e.g. `ncells=1024-hyper=1e-3`) crash the parser silently with misleading errors about missing definitions.
- **Profiling:** AMReX's TinyProfiler defaults to enabled (`tiny_profiler.enabled = true`, and Quokka's `CMakeLists.txt` forces `AMReX_TINY_PROFILE ON`, so the instrumentation is always compiled in). It prints a full per-region time breakdown at finalize, including communication routines (e.g. `FillBoundary_*`), aggregated across MPI ranks. This is the only way to measure actual comm-vs-compute overhead; the always-printed "Performance figure-of-merit" (Mupdates/s) is throughput only, no breakdown. Do not set it in a TOML: the value never varies, so declaring it adds nothing a reader doesn't already get from this default.
