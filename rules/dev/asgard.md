# Asgard Project Conventions

These rules apply when working within the Asgard project. They complement the general Python conventions in `python.md` and take precedence where they overlap.

---

## Repository Structure

### sindri

Personal python libraries live under `Asgard/sindri/submodules/`. Projects that are part of the Asgard ecosystem should be placed within this tree.

| Package | Purpose |
|---|---|
| `jormi` | shared utility library for computing MHD turbulence statistics: vector field decompositions, power spectra, PDFs |
| `bifrost` | stores scientific data efficiently and provides an interface for accessing it |
| `vegtamr` | line integral convolution library for vector field visualisation |
| `ww-arepo-sims` | interface between AREPO simulation data and jormi |
| `ww-flash-sims` | interface between FLASH simulation data and jormi |
| `ww-quokka-sims` | interface between Quokka simulation data and jormi |

jormi is the primary shared utility library. It covers the full workflow of scientific computing in the Asgard ecosystem: MHD turbulence statistics, field operations and decompositions, array utilities, plotting, I/O, logging, and HPC job scheduling. Before writing any new utility logic, check jormi first. New projects should depend on jormi and reuse what it offers rather than reimplementing it.

Beyond jormi, make use of the other submodules where relevant. If the work involves loading or processing simulation data, reach for the appropriate `ww-*-sims` package rather than writing bespoke I/O. For vector field visualisation, use vegtamr. Note that bifrost is still under active development and not yet functional; do not depend on it.

### freyja

freyja is the development sandbox. It brings together many personal packages in one place, used for prototyping and testing ideas before they are ready to be formalised. Code here is exploratory and not expected to be production-quality.

### mimir

Once a science idea is solid, it graduates to a dedicated science project repo under mimir. Each mimir repo is tied to a specific paper and contains the complete workflow for that paper: data processing, analysis, and figures. These repos are meant to be self-contained and reproducible.

---

### Referencing Personal Libraries

During active development, reference personal libraries as editable installs in `pyproject.toml`:

```toml
[tool.uv.sources]
<package-name> = { path = "../submodules/<package-name>", editable = true }
```

Once a project has matured and the dependency has stabilised, switch to a pinned git commit:

```toml
[tool.uv.sources]
<package-name> = { git = "https://github.com/AstroKriel/<package-name>", rev = "<commit-hash>" }
```

Do **not** add `[tool.hatch.metadata] allow-direct-references = true` when using `[tool.uv.sources]`. That flag is only needed when a direct URL reference is written inline in the `dependencies` list (e.g. `"jormi @ file://..."`). With `[tool.uv.sources]`, the `dependencies` list contains only a plain package name and hatchling never sees the path.

---

## Imports

Asgard projects extend the standard import order with two personal library groups, placed based on how the dependency is referenced:

| Group | Purpose |
|---|---|
| `## stdlib` | Python standard library |
| `## third-party` | external packages |
| `## personal (remote)` | personal libraries referenced as a pinned git commit |
| `## local` | imports from within the current project |
| `## personal (local)` | personal libraries referenced as an editable install |
