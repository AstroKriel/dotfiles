# Notes: HPC

Notes on HPC clusters you use but do not own or administer; each lives under `<project-notes>/hpcs/<cluster>/`.

---

## Structure

```text
hpcs/<cluster>/
├── README.md  # cluster reference sheet
├── log.md     # dated entries: outages, queue changes, module updates, workarounds
├── tasks.md   # open setup and documentation tasks
├── threads/   # focused investigations; same shape as project threads
└── <node>.md  # per-node deltas when nodes differ (hardware, node-local scratch, GPU)
```

`README.md` is the only required file; the rest are created when first needed.

---

## README.md

The reference sheet: everything needed to start a session from scratch.

| Section | Content |
|---|---|
| `## Instance` | Placeholder table for all account-specific values. Shared placeholders (`<username>`, `<home>`, `<repos>`) in one table; per-project storage paths under bold sub-labels (**`<project-code>:`**) with their own table. Name storage placeholders `<tier-project>` (e.g. `<scratch-<project-code>>`) so they are unambiguous when referenced elsewhere. Always include `<repos>`: the code checkout root, conventionally `~/repos/`. |
| `## Access` | Sanitized connection snippet using `## Instance` placeholders. `~/.ssh/config` stays in the setup repo. |
| `## Storage` | Storage tiers mapped to `home`/`fast-storage`/`project` concepts. |
| `## Software` | Non-standard module load sequences. Host-specific build steps as `### <codebase>` subsections. |
| `## Minimal Job Script` | One inline job script. Submission files for actual runs live in the run directory. |
| `## Codes` | Table of name, checkout path (using `<repos>`), and role. No remote URLs. Stub the section if no codes are installed yet. |
| `## Hardware` | Specs and filesystems for a single node; move to `<node>.md` when nodes diverge. |

---

## When something takes real work

Record each part once:

| Output | Goes to |
|---|---|
| Investigation trail | `threads/` |
| Dated reference back to the thread | `log.md` |
| Reusable result | the relevant README section |

---

## When nodes differ

- Each `<node>.md` holds only that node's deltas.
- Every shared fact lives once in `README.md`.
- The from-scratch bar is `README.md` plus the relevant node file.

---

## Out of scope

| Not here | Where instead |
|---|---|
| Output data from runs | cluster fast-storage |
| Project-specific analysis | project notes |
| Config and shell files | setup repo |
| Generic scheduler/module conventions | promote to `<rules>/` |

---

## tasks.md

Only open items; no ticked checkboxes, no reference material. When a task completes, move the fact to the relevant file and remove the task entry. Tasks pending an external party get a status note inline: contact, date sent, and what to verify once resolved.

---

## threads/

Open a thread when an investigation takes more than a few commands to resolve. Each thread `README.md`:

- Opens with the question being investigated.
- Records steps and what each ruled in or out.
- Closes with the resolution and where the finding was promoted.
- Resolved threads move to `threads/archived/`.

---

## Citing sources

- Every non-obvious factual claim carries its source: a link for web-sourced facts; a verifying command for machine-checked ones.
- A command citation beats a date: it shows how to re-verify, not just when someone last checked.
- For hardware or system fact tables, add a `> **Note:**` block after the table with a `| Purpose | Command |` verification table.

---

## Keeping notes current

- Update `README.md` when login details, storage paths, or scheduler configuration change.
- Log outages, unexpected queue behaviour, and environment changes that affected a run.
- Storage quota ceilings are README reference; log current fill levels instead.
- When a cluster is no longer in active use, add a final log entry and archive the directory.
