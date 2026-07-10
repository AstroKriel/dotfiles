# Quokka: Data Extraction and Diagnostics

How to extract simulation output and diagnose failed Quokka runs.

---

## Tool

**Package:** `ww-quokka-sims`

- Activate the virtual environment before running any command.
- The environment path is machine-specific; check `<project-notes>` for the current host.

---

## Workflow

| Rule | Detail |
|---|---|
| Diagnostics first | The diagnostic commands are the primary interface with simulation data; use them before writing any custom extraction code. |
| Plot on the host | When sim data lives on a remote host, run the diagnostic commands there. Copy only the diagnostics outputs back. |
| Post-analysis from diagnostics | For comparisons or derived quantities, load the extracted JSON/CSV data file from `diagnostics/`; do not re-read the plotfile. |
| Data over images | When `--save-data` has been run, all numerical conclusions must come from the saved data file. Do not read figure image files; figures are outputs for the user, not inputs for analysis. |

**Extraction:**

1. **Inspect.** Call `quokka-inspect-snapshot <plt_dir>` to confirm which field keys are available before running anything else.
2. **Extract.** Run the appropriate plot command with `--save-data`. This writes the figure and data to the sim's `diagnostics/` subdirectory. Raw plotfiles stay on the cluster or in `/tmp/`; only diagnostics products are committed.
3. **Sanity-check.** Run `quokka-plot-vi-evolution` to check volume-integrated energy and momentum before extracting detailed field data.

---

## Commands

| Command | Purpose |
|---|---|
| `quokka-plot-profiles` | Midplane 1D profiles of scalar or vector field components along any axis. |
| `quokka-plot-slices` | Midplane 2D slices of field components; auto-generates MP4 animations over a snapshot series. |
| `quokka-plot-pdfs` | Probability distribution functions of field components over a snapshot or series. |
| `quokka-plot-spectra` | Isotropic power spectra of scalar fields. |
| `quokka-plot-vi-evolution` | Volume-integrated field quantities as a time series. |
| `quokka-plot-vi-comparison` | Fractional difference in volume-integrated quantities between two simulation runs. |

---

## Flags

| Flag | Applies to | Meaning |
|---|---|---|
| `--tag` | all commands | Glob pattern to select a subset of plotfiles (e.g. `plt000*`). Omit to use all. |
| `-f` | plot commands | Field name(s) to extract (e.g. `magnetic`, `density`, `velocity`). |
| `-c` | profile, slice, pdf | Component index for vector fields: `x_0`, `x_1`, `x_2`. |
| `-a` | profile, slice | Axis along which to profile or slice (e.g. `x_0` for the x-axis). |
| `--save-data` | plot commands | Write extracted values alongside the figure. |
| `-o` | plot commands | Output directory for figures and data. |

---

## Field names

| Field name | What it is |
|---|---|
| `magnetic` | Magnetic field vector |
| `velocity` | Velocity vector |
| `density` | Gas density |
| `total_energy` | Total energy (internal + kinetic + magnetic) |


---

## Diagnosing a Failed Run

### Triage sequence

**1. Check for output.** Look for plotfiles in `snapshots/`. If none exist, go to [No output](#no-output).

**2. Plot what ran.** Run diagnostic commands on the HPC, directing output to a new `tmp/` subdirectory:

```bash
quokka-plot-vi-evolution -o <project>/tmp/vi-check/<YYYYMMDD>-initial
```

Pull only the figures locally and inspect visually.

**3. Dig deeper if needed.** If the volume-integrated quantities show a problem (blow-up, stall, unexpected drift), run further plot commands targeting the relevant fields. Pull figures only until the cause is clear.

**4. Use logs as secondary context.** Check `logs/` to confirm when the run stopped and whether it was a scheduler kill or a code exit.

### No output

If plotfiles were configured but none were written, the run failed before producing anything. Start with `logs/`:

- Config or TOML parsing errors appear at the top of the AMReX output.
- A missing file or bad path will error immediately on startup.
- A scheduler kill before the job started leaves no AMReX output at all; check the job accounting.
