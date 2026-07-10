# Quokka: MHD Configuration

How to configure Quokka for MHD simulations, covering TOML parameters, electromotive force (EMF) schemes, and MPI decomposition.

## Build requirement

`AMReX_SPACEDIM=3` is mandatory for all MHD problems. A 1D or 2D build silently omits all MHD targets with no warning. Changing `SPACEDIM` requires a fresh build directory.

---

## TOML parameters

AMReX exposes many parameters and often multiple ways to achieve the same thing. This section documents the preferred parameters and values for MHD runs, not an exhaustive reference.

**`geometry` / `quokka` (domain setup):**

| Parameter | Values | Notes |
|---|---|---|
| `geometry.prob_lo` | float array | Lower corner of the domain per dimension. |
| `geometry.prob_hi` | float array | Upper corner of the domain per dimension. Cell size follows: `dx = (prob_hi - prob_lo) / n_cell`. |
| `quokka.bc` | `"periodic"`, `"reflecting"` | Required. Boundary conditions for all fields. Reflecting boundary-condition support for magnetic fields is incomplete; use periodic for MHD tests. |

**`amr`:**

| Parameter | Recommended | Notes |
|---|---|---|
| `amr.n_cell` | int array | Number of cells per dimension. Sets resolution; `dx` follows from domain size. |
| `amr.max_level` | `0` | Single-level for most MHD tests. |
| `amr.blocking_factor_x` | `16` | See MPI decomposition below. |
| `amr.max_grid_size` | `128` | See MPI decomposition below. |
| `do_reflux` | `0` | Disable for single-level runs. |
| `do_subcycle` | `0` | Disable for single-level runs; also required off with any physical diffusion (e.g. `mhd.resistivity`); see Resistivity. |
| `plotfile_prefix` | `"snapshots/plt"` | Output path prefix for plotfiles; defaults to `plt` in the run working directory if absent. |

**`hydro`:**

| Parameter | Values | Notes |
|---|---|---|
| `hydro.rk_integrator_order` | `2` | Second-order Runge-Kutta (RK2) time integration. Standard for all MHD runs. |
| `hydro.reconstruction_order` | `1`, `2`, `3`, `5` | Spatial reconstruction order for hydro; see [Reconstruction schemes](#reconstruction-schemes). |
| `hydro.use_dual_energy` | `0` | Disable for MHD. |
| `hydro.artificial_viscosity_coefficient` | float, optional | Scalar viscosity coefficient; adds diffusive flux to momentum equations. Use to damp post-shock oscillations. |

**`mhd`:**

| Parameter | Values | Notes |
|---|---|---|
| `mhd.emf_compute_scheme` | `"FelkerStone2017"`, `"Balsara2025"`, `"Quokka2026"` | How edge-centred EMFs are computed from face-centred fluxes. |
| `mhd.emf_averaging_scheme` | `"LondrilloDelZanna2004"`, `"Balsara2025"` | How EMFs are averaged at shared edges between adjacent faces. |
| `mhd.emf_reconstruction_order` | `1`, `2`, `3`, `5` | Spatial reconstruction order for MHD; see [Reconstruction schemes](#reconstruction-schemes). Must match `hydro.reconstruction_order` in convergence tests. |
| `mhd.resistivity` | float, default `0` | Physical resistivity; enforces parabolic timestep limit `dt < dx^2 / (2 * eta)`. |

---

## EMF scheme reference

All three compute schemes are stable and comparable in accuracy; `Quokka2026` is the recommended default (fastest).

| Compute scheme | Notes |
|---|---|
| `Quokka2026` | Recommended default. |
| `Balsara2025` | Alternative. |
| `FelkerStone2017` | Well-validated reference. |

| Averaging scheme | Notes |
|---|---|
| `LondrilloDelZanna2004` | Standard upwind averaging. |
| `Balsara2025` | |

---

## Reconstruction schemes

Spatial reconstruction (interpolation) schemes, lowest to highest order. Set via `hydro.reconstruction_order` and `mhd.emf_reconstruction_order`.

| Value | Scheme | Reconstruction | Notes |
|---|---|---|---|
| `1` | PCM | piecewise-constant | Most diffusive. |
| `2` | PLM | piecewise-linear | |
| `3` | PPM | piecewise-parabolic | Can lose convergence at high resolution on smooth flows (the limiter clips smooth extrema). |
| `5` | PPM-EP | piecewise-parabolic, extremum-preserving | Most accurate; limiter preserves smooth extrema, so convergence holds for smooth flows. |

---

## Resistivity

Enable with `mhd.resistivity = <eta>`. The parabolic timestep limit is enforced automatically.

| Rule | Detail |
|---|---|
| No AMR subcycling with physical diffusion | Set `do_subcycle = 0` whenever `mhd.resistivity != 0`; Quokka aborts otherwise ("AMR subcycling is not supported with nonzero resistivity"). This holds for any physical diffusion term, so a future hydro viscosity carries the same restriction: subcycled parabolic operators need diffusive refluxing and time-interpolated coarse-fine boundary data, which is not implemented. |
| No resistivity in Richardson convergence tests | `FastWaveConvergence` and `SlowWaveConvergence` abort if `mhd.resistivity != 0`. Resistivity validation uses `AlfvenWaveLinear`. |
| Reference input | `inputs/AlfvenWaveLinear_resistive.toml` (eta=0.01, grid-aligned, FelkerStone2017 + LondrilloDelZanna2004). |
| Analytic reference | Amplitude decays as `exp(-gamma*t)` where `gamma = eta*k^2/2`. Velocity lags B by `phi = arctan(gamma/omega_real)`. |

---

## MPI decomposition

Setting `amr.blocking_factor_x` to `max(16, nx)` and `amr.max_grid_size` to `nx` forces a single AMReX box at every resolution, making all MPI ranks beyond the first idle with no warning. Always set:

```toml
amr.blocking_factor_x = 16
amr.max_grid_size = 128
```

This allows AMReX to split a 512-cell domain into up to 32 boxes.

---

## Minimum cell count

The hydro stencil uses `nghost = 4`. A single-box periodic grid below 8 cells per dim has opposite-side ghosts overlapping inside the valid region. Use at least 8 cells per dim under periodic boundary conditions.
