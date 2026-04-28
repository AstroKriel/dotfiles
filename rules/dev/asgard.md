# Asgard Project Conventions

These rules apply when working within the `Asgard/` project. They complement the general Python conventions in the neighbouring `python/` directory and take precedence where they overlap.

---

## Repository Structure

### sindri

Python libraries live under `Asgard/sindri/submodules/`. Projects that are part of the `Asgard/` ecosystem are placed within this tree.

| Package | Purpose |
|---|---|
| `jormi/` | shared utility library for computing MHD turbulence statistics: vector field decompositions, power spectra, PDFs |
| `bifrost/` | stores scientific data efficiently and provides an interface for accessing it |
| `vegtamr/` | line integral convolution library for vector field visualisation |
| `ww-arepo-sims/` | interface between AREPO simulation data and `jormi/` |
| `ww-flash-sims/` | interface between FLASH simulation data and `jormi/` |
| `ww-quokka-sims/` | interface between Quokka simulation data and `jormi/` |

`jormi/` is the primary shared utility library. It covers the full workflow of scientific computing in the `Asgard/` ecosystem: MHD turbulence statistics, field operations and decompositions, array utilities, plotting, I/O, logging, and HPC job scheduling. It is the first point of reference for any new utility logic; new projects depend on it rather than reimplementing what it covers.

#### Internal layering

`jormi/` enforces a strict two-layer separation between array math and field objects:

- `ww_arrays/` owns all array-level mathematics. Functions here operate purely on `NDArray` inputs and return `NDArray` outputs. No field objects, no field metadata.
- `ww_fields/` is a thin wrapper layer. It extracts arrays from field objects, delegates to `ww_arrays/`, and rewraps the result. It contains no array math of its own.

New computations are implemented in `ww_arrays/`. The `ww_fields/` wrapper calls them. A computation belongs in `ww_arrays/` even when only used inside `ww_fields/`, unless it is trivially one line.

Beyond `jormi/`, the other submodules are used where relevant. Simulation data loading and processing uses the appropriate `ww-*-sims/` package. Vector field visualisation uses `vegtamr/`.

> **Note:** `bifrost/` is still under active development and not yet functional.

### freyja

`freyja/` is the development sandbox. It brings together many packages in one place, used for prototyping and testing ideas before they are ready to be formalised. Code here is exploratory and not expected to be production-quality.

### mimir

Once a science idea is solid, it graduates to a dedicated science project repo under `mimir/`. Each `mimir` repo is tied to a specific paper and contains the complete workflow for that paper: data processing, analysis, and figures. These repos are self-contained and reproducible.

---

## Data Representation

Simulation interface layers preserve the representation of the data as read from disk. If the source data are `float32`, loaders return `float32` fields by default rather than silently casting/promoting to `float64`.

Numerical promotion belongs in the computation layer (`jormi/`). When an operation requires higher precision for correctness or stability, the compute-side implementation converts or promotes the relevant arrays there. Precision promotion is not the responsibility of project code in `mimir/`.

---

## Imports

Asgard projects extend the standard import order with two additional library groups, placed based on how the dependency is referenced:

| Group | Purpose |
|---|---|
| `## stdlib` | Python standard library |
| `## third-party` | external packages |
| `## personal (remote)` | personal libraries referenced as a pinned git commit |
| `## local` | imports from within the current project |
| `## personal (local)` | personal libraries referenced as an editable install |

---

### Referencing Personal Libraries

During active development, personal libraries are referenced as editable installs in `pyproject.toml`:

```toml
[tool.uv.sources]
<package-name> = { path = "../submodules/<package-name>", editable = true }
```

Once a project has matured and the dependency has stabilised, personal libraries are referenced as a pinned git commit:

```toml
[tool.uv.sources]
<package-name> = { git = "https://github.com/<username>/<package-name>", rev = "<commit-hash>" }
```

`[tool.hatch.metadata] allow-direct-references = true` is not needed when using `[tool.uv.sources]`. That flag is only needed when a direct URL reference is written inline in the `dependencies` list (e.g. `"jormi @ file://..."`). With `[tool.uv.sources]`, the `dependencies` list contains only a plain package name and hatchling never sees the path.

---

## Terminal Feedback

User-facing terminal feedback in Asgard projects uses `jormi.ww_io.manage_log`. This covers actions, progress messages, warnings, summaries, skipped work, created/saved files, validation-script pass/fail status, and other operational messages intended for a person reading the terminal.

Pure compute helpers, low-level transformations, and routine internal state do not use `manage_log`; they return values or raise exceptions. Raised exceptions are not replaced with logging unless the function is responsible for handling the error and continuing.

Direct terminal output is limited to: the logger implementation itself, generated shell-script content, and raw child-process output streamed by a subprocess helper. `print()` is not used for user-facing feedback; functions accept a `verbose` flag when a message is optional.

### Log functions

All messages: lowercase throughout; names and identifiers in backticks, runtime data bare. No redundant prefixes (`"Note:"`, `"Warning:"`, `"Error:"`) in messages.

| Function | When to use | Form |
|---|---|---|
| `log_section` | major phase boundary in script output | noun phrase title; no period |
| `log_context` | current parameters or config at the start of a run | noun phrase title; no period |
| `log_task` | before a long-running operation starts | present participle: `"reading file: {path}"`; no period |
| `log_note` | neutral observation worth surfacing (e.g. timing, counts) | sentence or noun phrase; period |
| `log_items` | enumerate a list of things under a title | noun phrase title; noun phrases or short sentences as items; no period |
| `log_hint` | non-fatal issue; data clipped, parameter ignored, fallback applied | sentence; period |
| `log_alert` | something unexpected that may indicate a problem but does not stop execution | sentence; period |
| `log_warning` | soft error condition; pairs with `raise_error=False` | sentence; period |
| `log_error` | non-raising failure; operation failed but execution continues | sentence; period |
| `log_action` | completed operation with outcome, title, and optional notes | noun phrase title; sentence message |
| `log_outcome` | pass/fail result for an individual vtest case | noun phrase; no period |
| `log_summary` | end-of-run summary with key metrics | noun phrase title; key-value notes, values bare; no period |
| `log_debug` | temporary verbose detail; remove once the issue is resolved | sentence; period |
