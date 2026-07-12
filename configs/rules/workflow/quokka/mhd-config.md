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
| `amr.max_level` | `0` | Single-level for most MHD tests. See [Multi-level AMR](#multi-level-amr) if raising this. |
| `amr.blocking_factor_x` | `16` | See MPI decomposition below. |
| `amr.max_grid_size` | `128` | See MPI decomposition below. |
| `do_reflux` | `0` | Disable for single-level runs; must be `1` for MHD once `amr.max_level > 0`, see [Multi-level AMR](#multi-level-amr). |
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

## Multi-level AMR

Setting `amr.max_level > 0` adds a constraint beyond the MPI-decomposition sizing above: Quokka's own startup check (`amrex::ProperlyNested` in `simulation.hpp`) aborts ("Grids not properly nested!") if `amr.blocking_factor_*` is too small, independent of the single-box ghost-cell concern below.

- **`do_reflux` must be `1` for MHD, not `0`:** the `EdgeFluxRegister` coarse-fine EMF correction that keeps `div(B)` consistent across refinement boundaries (see GitHub issue quokka-astro/quokka#530) is entirely gated behind `do_reflux != 0` (`QuokkaSimulation::advanceSingleTimestepAtLevel`). Copying `do_reflux = 0` from the single-level convention above silently disables this correction: the run looks fine at first, then catastrophically diverges (density collapsing towards zero, velocity exploding past `1e30`) the moment a refined feature actually crosses a coarse-fine boundary, reproducibly at the same location and time regardless of EMF scheme or reconstruction order. Quokka's own working AMR+MHD test (`inputs/MHDBlast.toml`) sets `do_reflux = 1` for exactly this reason; a uniform-grid (`amr.max_level = 0`) run of the same problem is unaffected, which is the fastest way to confirm this is the cause before spending time elsewhere (buffer tuning, EMF scheme, reconstruction order all failed to fix it; `do_reflux = 1` did).
- **Blocking factor floor:** the abort message suggests `blocking_factor >= ceil(nghost_cc, ref_ratio) * ref_ratio`, but this understates the real minimum: `blocking_factor = 8` failed empirically for a `Quokka2026` run (`nghost_cc = 7`, formula gives `8`). `16` is the smallest value confirmed to work; use it as the default floor for any `amr.max_level > 0` run regardless of EMF scheme.
- **`max_grid_size` must stay a multiple of `blocking_factor`:** same AMReX-wide rule as the single-level case, but now bounded below by the floor above; this caps how many boxes (and therefore MPI ranks) a given resolution can support once AMR is on.
- **More ranks needs more domain cells, not a smaller blocking factor:** once `blocking_factor` is at the floor, the only way to add boxes is to add `amr.n_cell`. That roughly multiplies total compute cost, so it is not a reliable way to reduce wall-clock; a small AMR test problem may simply have a low MPI-rank ceiling.

---

## Minimum cell count

The hydro stencil uses `nghost = 4` as a baseline; MHD adds `nghost_Riemann` on top (`nghost_cc = nghost_Riemann + 4`), which depends on `mhd.emf_compute_scheme`: `3` for `Quokka2026`, otherwise `1` (`LondrilloDelZanna2004` averaging) or `2` (`Balsara2025` averaging) via `mhd.emf_averaging_scheme`. A single-box periodic grid below 8 cells per dim has opposite-side ghosts overlapping inside the valid region. Use at least 8 cells per dim under periodic boundary conditions.
