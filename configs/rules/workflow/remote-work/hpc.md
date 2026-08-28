# Remote Work: HPC Workflow

How to work on HPC clusters, covering onboarding, module loading, job submission, and data management.

---

## Storage Tiers

| Concept | Role | Typical names |
|---|---|---|
| `home` | Persistent, backed up, small quota; for configs and code checkouts | `/home/<user>` |
| `fast-storage` | High-throughput, large capacity, not backed up; for active runs and outputs | `scratch`, `work`, `lustre`, `nobackup` |
| `project` | Shared with collaborators, larger quota; not available on all clusters | `project`, `group` |

When working on a specific cluster, resolve these concepts from the cluster notes before acting.

---

## Home Repo Layout

`<repos>` always resolves to `~/repos`: a fixed convention, not cluster-specific vocabulary to redefine per cluster note.

Checkouts split by type, the same two names on every cluster:

| Type | Holds | Examples |
|---|---|---|
| `sim-codes/` | Simulation codebases: compiled, built, and run to produce data | `quokka`, `pencil-code` |
| `python-analysis/` | Python packages for diagnostics, plotting, and post-processing | `ww-quokka-sims`, `jormi` |

```text
~/repos/
├── sim-codes/
│   └── <code>/
└── python-analysis/
    └── <package>/
```

Git worktrees follow the same sibling convention as local machines (see [`<rules>/workflow/git/worktrees.md`](../git/worktrees.md)): `sim-codes/<code>-worktrees/<branch-slug>/` sits alongside `sim-codes/<code>/`.

---

## Onboarding a New Cluster

When access to a new cluster is gained:

1. Create the cluster notes at `<project-notes>/hpcs/<cluster>/` following [`<rules>/workflow/note-taking/hpc.md`](../note-taking/hpc.md)
2. Add a host entry to `~/.ssh/config` per `./ssh.md`
3. Log in and identify the available storage tiers; map each to its actual path
4. Survey the module environment: compiler toolchain, MPI, HDF5/parallel I/O stack
5. Submit a minimal test job to verify scheduling and I/O work
6. Record the storage tier paths and working module stack in the cluster `README.md`
7. Write the same tier paths to `~/storage_paths.txt` on the cluster, for quick lookup

---

## Job Scripts

Directives are scheduler-specific (SLURM uses `#SBATCH`, PBS uses `#PBS`); check the cluster `README.md` for the scheduler type.

**Naming:** `<project>-<descriptor>`, short enough to read in the queue.

**Working directory:** invoke the submission command (`sbatch`/`qsub`) from inside the sim's own directory, or set the working directory explicitly to it with `--chdir` (SLURM) or `-d` (PBS). The scheduler drops stdout/stderr logs wherever the working directory resolves to (PBS's `-l wd`, for instance, uses wherever `qsub` was called from); submitting from anywhere else (home, a shared scripts folder) scatters logs away from the run they belong to, with no way to tie them back together later. Never rely on submission directory or home directory defaults without checking where that actually resolves to.

**Module loading:** always `module purge` before loading. Pin the full module string (name and version) from the cluster `README.md` and use it verbatim across all jobs for that cluster. Log any version changes in `log.md`.

**Checkpointing for wall-time-limited jobs:** For jobs that may run close to the partition's wall time limit, enable checkpointing at a coarse enough cadence that one or two checkpoints exist before the job ends. This allows a restart from near the cutoff rather than from the beginning.

**Validate before chaining:** Before submitting a build-then-run dependency chain (`sbatch --dependency=afterok:$BUILD_ID`), run the build step once in a short interactive or devel allocation first. A failing build marks all downstream jobs as `DependencyNeverSatisfied` with no diagnostic; the queue shows the symptom, not the cause, and jobs sit there burning wait time.

**Short test job before production at untested scale:** When the cluster's short or interactive queue runs ahead of the production queue, use a short test job (~100 steps) to validate an untested resolution or node count before tying up a long-queue slot. Check the application's startup output for the expected resource counts (MPI ranks, GPU devices); a misconfigured allocation can let the job start and run silently wrong.

---

## Module Architecture

On clusters with mixed CPU architectures, module system packages may be compiled for a specific ISA. A module-provided binary can crash with `SIGILL` on a node with a different architecture, even if it loaded cleanly on the login node.

Before relying on a module-provided binary for a build tool (e.g., make, ninja, ar, ranlib), verify it matches the architecture of the node where the build will run (`module show <name>` shows the build provenance). When in doubt:

- Use system binaries for low-level tools (e.g., `/usr/bin/ar`)
- Use portable installs for build drivers (e.g., `pip install --user ninja` installs a `manylinux` wheel that is portable across all x86_64 nodes)
- Record the working tool choices in the cluster notes

---

## Run Directory Layout

`home` holds only version-controlled source checkouts, nothing else. Everything memory- or storage-heavy (builds, sim data, logs) lives on `<fast-storage>`, scoped under the science project it belongs to. Something with no owning project doesn't get a permanent home at all; see "Builds under active development" below.

Simulations go under `<fast-storage>/<science-project>/<codebase>/`. Resolve `<fast-storage>` from the cluster's `## Instance` section before acting; on clusters with multiple allocation projects it maps to a project-specific placeholder (e.g. `<scratch-jh2>`), giving a full path of `<scratch-jh2>/<science-project>/<codebase>/`. Note that `<science-project>` is the research project name (e.g. `mhd-turbulence`), not an allocation project code.

The `<codebase>` level applies even when a project currently uses only one code: it keeps the shape consistent if a second code is ever added, and gives a project-owned build a natural home next to the data it produced (see "Builds under active development" below). A project using two codes gets two clean subtrees instead of concepts and sim names interleaved from both.

Sim directories are grouped by scientific concept; each sim directory is self-contained (no symlinks) so it can be moved or archived without breaking.

A sim's home is always `sims/<concept>/<sim-name>/`: a superseded attempt and a baseline still cited in the analysis both live there, distinguished only by a `<sim-name>` that says what each one is (e.g. `1024-baseline-plm-ppm`). A run that stops being needed for anything gets deleted from that path, not relocated to a separate archive tier.

| Concept | Role | Name defined by |
|---|---|---|
| `<sim-inputs>` | Config and input files the simulation reads | Code rules |
| `<sim-executable>` | Copy of the built binary the sim was run with (out-of-source builds only) | Code rules |
| `<sim-outputs>` | Raw output written by the simulation | Code rules |
| `<derived>` | Reduced data from analysis tools; what gets transferred locally | Code rules |

```text
<project>/
├── <codebase>/
│   ├── sims/
│   │   └── <concept>/
│   │       └── <sim-name>/
│   │           ├── jobs/
│   │           ├── <sim-inputs>
│   │           ├── <sim-executable>
│   │           ├── logs/
│   │           ├── <sim-outputs>/
│   │           └── <derived>/
│   └── builds/
│       └── <branch-slug>/<config>/
└── tmp/
```

`jobs/` and `logs/` live inside each `<sim-name>/`, never in a shared location: submit every job from inside that sim's own directory (see "Working directory" above) so the scheduler's logs land there automatically, co-located with the run they belong to.

`tmp/` follows the same concept and naming conventions as `~/tmp/` in [`<rules>/workflow/asgard/project.md`](../asgard/project.md), but on remote systems it lives under `<fast-storage>/<project>/`, not under `~`. Placing it on `home` consumes the small quota and causes usage spikes.

---

## Code Deployment

Deploy only what the cluster needs to execute the job: typically the project repo or the relevant `ww-*-sims` interface layer. Record what was deployed and any build steps in the cluster `log.md`.

### Syncing source changes: git, not rsync

Make code changes **locally**, commit, and push; then bring them to the remote with `git pull` (or `git fetch` + `git reset --hard origin/<branch>` when the remote working tree has stray edits). **Never `rsync`/`scp` source files between local and a cluster checkout.** Doing so desyncs the working tree from git history, breaks output provenance (the build no longer corresponds to a commit), and silently diverges the two trees. This applies to source code only; output data still comes back via the Data Transfer rules below.

### Source, builds, and data

| Artifact | Tier | Why |
|---|---|---|
| Source checkout | `home` (or a shared tier) | One checkout per cluster; small, version-controlled, shared across nodes. |
| Build tree | `fast-storage` (node-local) | Heavy artifacts stay off the small `home` quota, and a build can be node- or GPU-specific. Never build into `home`. |
| Run data | `fast-storage` | Bulk output; not backed up. |

Each project's notes declare where its data and builds live on each cluster, in a `## Data and builds` section of the project `README.md`, so locations stay discoverable.

### Builds under active development

Where a build lives depends on one question: does this work belong to a specific science project, or is it codebase development/maintenance with no project attached?

- **No owning project** (a feature branch or a bug fix: work that's bound for the codebase itself, not for a specific paper or investigation): the build lives under `<codebase>/threads/<branch-slug>/build/<config>`, scoped to the branch alone. This is ephemeral scaffolding, not data, so it never gets a permanent reserved directory: create it when the thread starts, delete it the moment the thread is shelved or merged. Validation/smoke sims for that thread live alongside the build, under `<codebase>/threads/<branch-slug>/sims/<purpose>/<problem>/` on `fast-storage`, never inside the source worktree on `home`.
- **Belongs to a project**: the build lives under `<project>/<codebase>/builds/<branch-slug>/<config>/` instead, named to match the source worktree's branch-slug exactly. Keep only what's currently needed: a sim already logs its own build provenance internally, so the build tree isn't the record of what produced a given result; once a build is superseded or no longer needed, delete it.

Either way:

- For out-of-source build systems (e.g. CMake), one source checkout is kept and each build tree lives on `fast-storage`, configured against that source on the relevant branch. Once a sim's build is ready to run, copy the built executable into the sim's own directory as `<sim-executable>`: the sim then stays self-contained and movable even after the originating build tree is superseded or deleted.
- For codes where the build is the run directory (compile-time grid or modules baked in per run), each run directory is its own build, grouped the same way.
- A single source checkout is on one branch at a time; a build is valid only while that branch is checked out.
- A matured project that pins a code version replaces a rolling build with one frozen build at the pinned commit, still under the project's own `builds/`.

---

## Data Transfer

- Transfer only reduced data to a local machine; never transfer raw output.
- Use `rsync` and preserve directory structure.
