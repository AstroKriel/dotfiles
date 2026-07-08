# Notes: Project

Notes on active research and teaching projects; each lives under `<project-notes>/`.

---

## Scope

A project note covers the context, status, tasks, and accumulated knowledge for a single research paper, teaching project, or supervision case.

Covered by this file:

| Category | Location |
|---|---|
| Research projects (lead author) | `<project-notes>/research/lead-author/<project>/` |
| Student supervision | `<project-notes>/research/student-projects/<student>/` |
| Teaching projects | `<project-notes>/teaching/<teaching-project>/` |
| Tools | `<project-notes>/tools/<tool>/` |

---

## Structure: Research Projects

Start with just `README.md`. Add files only as the project grows. Two guiding principles:

- The entry point for any folder is always `README.md`.
- A file splits into a folder of the same name when its content spans multiple domains or grows too large (the top rung of the structure ladder in [`writing/markdown.md`](../../writing/markdown.md)).

```text
<paper>/
├── README.md      # overview; becomes index as project grows
├── log/           # session trail; one file per session named YYYY-MM-DD.md
├── tasks.md       # task list; splits into tasks/ when tasks span multiple domains
├── threads/       # active explorations and open questions
│   └── archived/  # resolved threads
└── notes/         # refs, background material, stable context
```

### README.md

The README is the entry point. It should orient anyone landing cold: what the project is, where to find things, and where to look for supporting context. For compute-heavy projects it includes three standard sections:

- `## Context`: pointers to the HPC notes, codebase notes, and rules that the project depends on. For anything inside `<project-notes>/`, write the path root-relative as `<project-notes>/<path>` (not relative to the file the pointer sits in); use `<rules>/<path>` for rules. Do not use absolute machine paths.
- `## Machines`: one row per machine, with its role in the project (e.g. which runs go where).
- The task and thread index sections that link to `tasks/` and `threads/`.

### threads/

Each thread is a standalone investigation that can be shared on its own:

- it is a subfolder with `README.md` and, if needed, `figures/`, `analysis/`, and a minimal `reproducer/` (config snippets or fixtures, never source or run results);
- if it has analysis scripts, it carries a self-contained `uv`-managed environment (`pyproject.toml` + `uv.lock`, with `.venv/` gitignored) so they run via `uv run`; shared libraries (e.g. `jormi`) are pinned to a git commit, never a local path, so the environment reconstructs wherever the thread is shared;
- it inherits no context from the rest of `<project-notes>`: it states any background the reader needs, and references other threads by folder name in backticks (e.g. `<thread-name>/`), not by relative path, so the reference survives archiving;
- its `README.md` opens with `**Opened:**` and, once settled, `**Resolved:**` dates, followed by quick-reference metadata fields (`**Status:**`, `**Branch:**`, `**PR:**`, or similar); these fields are the only content updated in place as state changes; for a resolved thread, one sentence of plain prose after `**Resolved:**` states the conclusion (written once, not updated); the `## Summary` section is written once on opening and not required to be kept current; progress is logged by appending dated `### YYYY-MM-DD:` sections -- the thread grows by appending, never by rewriting, and the deduction story (the chain of observations and what each ruled in or out) emerges from these sections rather than from a separate narrative;
- resolved threads move to `archived/`, with the index entry updated to the resolved status and date; a conclusion carried out of a thread must not be stated more broadly than the thread established.

Figures not tied to a thread belong in the project repo, not `<project-notes>`.

### log/

The log is an append-only session trail: each file (`YYYY-MM-DD.md`) is a snapshot of one session's understanding at that moment. Notes and threads evolve; the log does not.

- Some duplication with notes is expected: if a finding first surfaces in a log entry, it belongs there even if it later appears in notes or threads.
- Omit stable reference material (parameters, storage paths, naming conventions); that belongs in `notes/`.

---

## Structure: Student Supervision

```text
<student>/
├── README.md  # who, project summary, degree milestones, current status
├── tasks.md   # current tasks for student and supervisor
├── log/       # dated meeting notes; one file per meeting named YYYY-MM-DD.md
└── notes/     # reference material (project description, setup details, etc.)
```

---

## Tasks and Notes Pairing

Applies wherever a project has a task list and a `notes/` directory: research (lead-author and student supervision) and teaching projects alike, not student supervision only. The task list is `tasks.md` before it splits, `tasks/<topic>.md` after.

When a project grows a `tasks/` folder, the `notes/` folder grows a matching file for each topic. The two files for the same topic are complementary: `tasks/<topic>.md` holds only active and pending work; `notes/<topic>.md` holds the durable record of what exists or has been done.

The lifecycle of a piece of work:
1. It starts as a task in `tasks.md` (or `tasks/<topic>.md` once split).
2. When it completes, its record moves to `notes/<topic>.md` (or the project's single `notes.md`-equivalent file before that splits); the entry is removed, not just marked done.
3. The task list shrinks over time. `notes/` grows.

A task list that is nothing but completed entries is a sign the notes file is missing or out of date.

**What goes in `notes/<topic>.md`:**

- Organise by subject, then by system or subsystem (e.g. HPC cluster, machine, or environment) as subsections.
- Each dataset or run is recorded with its parameters listed as an itemised list before any table of runs. Parameters include resolution, stop time, plot interval, scheme, Mach number, and any other values a reader would need to reproduce or interpret the data.
- Contextual remarks and caveats following a table go in a `> **Note:**` blockquote, not as inline prose.
- Storage paths, naming conventions, and machine-assignment rationale belong here, not in tasks.

**What stays in `tasks/<topic>.md`:**

- Uncompleted items only. No reference material, no completed items, no storage layout docs.
- A brief status line at the top noting current priority and what is blocked or in flight.

---

## What belongs here

| Belongs | Does not belong |
|---|---|
| Current status and open questions | Line-by-line code documentation |
| Key findings and decisions | Raw simulation output |
| Task lists | Configuration files (those go in the project repo) |
| Notes on sources and references | Working conventions (promote to `<rules>/`) |
| Reproduction steps for a result | |

---

## Concluding a project

Add a final log entry marking the outcome (accepted, rejected, etc.) and archive the directory. Do not delete it.
