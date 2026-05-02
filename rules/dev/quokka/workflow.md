# Quokka: Local Workflow

Working notes for local Quokka development: CMake build trees, the `scripts/bash/quokka` wrapper, the two-tier compute model, and the current native workflow on an Arch AMD laptop.

---

## Environment Layers

Two layers are involved in day-to-day Quokka work:

| Layer | Purpose | Example |
|---|---|---|
| CMake build tree | stores one compiled Quokka configuration: cache, generated build files, and binaries | `build/1d-release`, `build/3d-release`, `build/3d-debug` |
| Container or devcontainer | provides a whole machine-level toolchain and OS environment | `.devcontainer/gcc-container` |

Quokka has an optional embedded Python feature (`QUOKKA_PYTHON`). It is always disabled (`-DQUOKKA_PYTHON=OFF`) because it is a separate failure surface from the solver and is not needed. All analysis and plotting is done externally via `ww-quokka-sims/` in the Asgard ecosystem.

There is no Python environment inside `quokka/`. Do not create one.

---

## Current Local Baseline

Current native baseline on the local Arch AMD laptop:

| Area | State |
|---|---|
| CPU toolchain | works |
| MPI | required; installed for native Quokka builds |
| `3d-release` MHD validation | active development target |
| ROCm/HIP | not part of the current workflow |

---

## Two-Tier Compute Model

Quokka work is split across two tiers:

| Tier | Machine | Purpose |
|---|---|---|
| Local | Arch AMD laptop | low-resolution 3D tests for development validation |
| HPC | supercomputer via SSH | production simulations at full resolution |

Local runs validate solver behaviour cheaply. HPC runs produce the data that feeds into analysis. Input `.toml` files are the same across both tiers; resolution and domain size are adjusted via the input file parameters.

---

## Data Pipeline

Quokka writes HDF5 plotfiles. These are the handoff point between the solver and the analysis layer:

```
Quokka (C++) -> HDF5 plotfiles -> ww-quokka-sims/ -> kriel-quokka-mhd
```

- `ww-quokka-sims/` is the interface layer that reads Quokka output. It lives in the Asgard ecosystem and the Asgard rules apply to it.
- `kriel-quokka-mhd` is the science project that consumes `ww-quokka-sims/` for analysis and figures.
- No analysis or plotting is done inside `quokka/` itself.

---

## The `quokka` Wrapper

`scripts/bash/quokka` is a thin repo-specific wrapper around normal CMake, Ninja, and CTest commands. It is convenience tooling, not a custom build system.

| Command | What it does |
|---|---|
| `quokka config` | configure a build tree with CMake |
| `quokka build` | compile one or more targets with Ninja |
| `quokka run` | run a built problem executable or a CTest selection |
| `quokka buildrun` | build and then run |
| `quokka list` | list problem directories under `src/problems/` |
| `quokka target` | print the raw CMake target list for a configured build tree |

The preset names are fixed:

| Preset | Build dir | Meaning |
|---|---|---|
| `3d` | `build/3d-release` | 3D Release |
| `3d-debug` | `build/3d-debug` | 3D Debug |

`quokka target` prints the full raw CMake target list and is usually too noisy for daily use. Prefer `quokka list`, direct problem names, or `quokka build --filter '<glob>'`.

---

## What `config`, `build`, and `run` Mean

Typical sequence:

1. `config` creates or refreshes a build tree.
2. `build` compiles a selected Quokka problem.
3. `run` executes the compiled problem with its default input file unless `--input` is given.

Example:

```bash
cd ~/Projects/quokka
scripts/bash/quokka config -d 3d --delete -DQUOKKA_PYTHON=OFF
scripts/bash/quokka build -d 3d AlfvenWaveLinear
scripts/bash/quokka run -d 3d AlfvenWaveLinear
```

What each line does:

| Command | Effect |
|---|---|
| `config -d 3d --delete -DQUOKKA_PYTHON=OFF` | recreates `build/3d-release` as a fresh 3D Release build tree with embedded Python disabled |
| `build -d 3d AlfvenWaveLinear` | compiles the `AlfvenWaveLinear` target in `build/3d-release` |
| `run -d 3d AlfvenWaveLinear` | runs that executable using `inputs/AlfvenWaveLinear.toml` by default |

---

## Recommended Native Workflow

Current recommended native workflow:

1. Use `3d-release` CPU builds for MHD development validation.
2. Delay ROCm/HIP until the `3d-release` CPU workflow is stable and local GPU validation is actually needed.

For the first `3d-release` MHD check:

```bash
cd ~/Projects/quokka
scripts/bash/quokka config -d 3d --delete -DQUOKKA_PYTHON=OFF
scripts/bash/quokka build -d 3d AlfvenWaveLinear
scripts/bash/quokka run -d 3d AlfvenWaveLinear
```

---

## MHD-Focused Problem Selection

For local MHD work, a lighter targeted test is better than a broad target dump or a full heavy 3D sweep.

Current useful problem names:

| Problem | Use |
|---|---|
| `AlfvenWaveLinear` | first local 3D MHD validation target |
| `AlfvenWaveLinearConvergence` | follow-up convergence-oriented MHD check |
| `OrszagTang` | stronger MHD follow-up after the Alfven-wave check |
| `MHDBalsaraVortex` | additional 3D MHD validation |

Relevant inputs include:

| Input file | Purpose |
|---|---|
| `inputs/AlfvenWaveLinear.toml` | default input for `AlfvenWaveLinear` |
| `inputs/AlfvenWaveLinearConvergence.toml` | default input for `AlfvenWaveLinearConvergence` |
| `inputs/alfven_wave_linear_regression.toml` | additional regression-style input |

`AlfvenWaveLinear` is the preferred first local `3d-release` MHD test because it is narrow, relevant, and cheaper than broader MHD problems.

---

## Build Variants

The `quokka` wrapper only supports the fixed preset names above. It does **not** provide arbitrary custom config names.

This means:

| Need | Use |
|---|---|
| standard 3D Release build | `-d 3d` -> `build/3d-release` |
| standard 3D Debug build | `-d 3d-debug` -> `build/3d-debug` |
| multiple different 3D Release variants | separate raw CMake build dirs with explicit mode names |

If multiple `3d` variants are needed, use raw CMake with explicit build directories:

```bash
cd ~/Projects/quokka
cmake -S . -B build/3d-release -G Ninja -DCMAKE_BUILD_TYPE=Release -DAMReX_SPACEDIM=3
cmake -S . -B build/3d-debug -G Ninja -DCMAKE_BUILD_TYPE=Debug -DAMReX_SPACEDIM=3
cmake -S . -B build/3d-asan -G Ninja -DCMAKE_BUILD_TYPE=Debug -DAMReX_SPACEDIM=3 -DENABLE_ASAN=ON
cmake -S . -B build/3d-werror -G Ninja -DCMAKE_BUILD_TYPE=Release -DAMReX_SPACEDIM=3 -DWARNINGS_AS_ERRORS=ON
```

Use custom build directories when compiler flags, sanitizers, or special debug options need to exist side by side.

---

## Lessons Learned

- `3d-release` CPU validation is the baseline for MHD work.
- Embedded Python (`QUOKKA_PYTHON=ON`) is a separate failure surface from the solver. Always disable it.
- `quokka target` is too noisy for normal use; direct problem names and a few known MHD problems are more useful.
- Keeping separate build trees per meaningful configuration is normal CMake practice, not Quokka-specific complexity.
- The `quokka` wrapper is repo-specific convenience, but the underlying workflow is general CMake, Ninja, and CTest practice.
