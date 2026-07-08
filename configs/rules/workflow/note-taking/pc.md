# Notes: Personal Machine

Notes on machines you own and maintain; each has a setup repository and a research reference entry.

---

## Scope

Personal machine notes have two forms, serving different purposes:

**Setup repository**: a standalone repo in `SystemNotes/` that records the configuration, installation history, and operational knowledge for one owned machine. It is the reproduction manual for that machine: following it from a clean install should reproduce the working configuration.

**Research reference entry**: a lightweight reference sheet at `<project-notes>/pcs/<machine>/README.md`, analogous to an HPC reference sheet. It records the machine's role in the research workflow and which code checkouts live on it. It does not duplicate setup steps or config details; those belong in the setup repository. The reference entry is what to consult during active research; the setup repository is what to consult when (re)configuring the machine.

Both forms are distinct from HPC notes (see [`hpc.md`](hpc.md)): HPC notes record how to use a shared cluster; personal machine notes record how a machine is configured and used.

---

## Structure

### Setup repository

```text
SystemNotes/<machine>/
├── README.md          # machine name, purpose, pointer to each partition
├── system-details.md  # hardware summary; omit for a single-OS machine and put it in README.md instead
└── <partition>/        # one directory per OS partition; omit this level for a single-OS machine and nest everything below directly under <machine>/
    ├── README.md          # partition overview; indexes the setup docs below once setup.md splits
    ├── setup.md           # installation steps: OS, packages, configs, services
    ├── pending-issues.md  # open issues and unresolved configuration problems
    ├── notes/             # distilled facts about how subsystems work on this machine
    │   └── <topic>.md     # one file per topic area; updated in place as understanding deepens
    └── debug-diary/       # retrospective entries for resolved issues
        └── YYYY-MM-DD.md  # one file per resolved issue
```

Introduce the `<partition>/` level only when a machine hosts more than one OS install; a single-OS machine keeps the flat layout this replaced.

| Belongs | Does not belong |
|---|---|
| Hardware specs and OS version | Config files themselves (those go in `<system-configs>/`) |
| Package and service installation steps | Project data or results |
| Non-obvious configuration decisions | HPC cluster details (see [`hpc.md`](hpc.md)) |
| Open and resolved configuration issues | Binding conventions (promote to `<rules>/`) |

### pending-issues.md

- Scope: currently open issues; unresolved problems, known workarounds in place, configuration gaps.
- Live document: entries are added and removed as issues open and close.
- Every active workaround entry must include a concrete test command under "Next steps" (defines the pass/fail condition for post-update checks).

### debug-diary/

- Append-only: each file records a resolved issue, its cause, and the fix; never edited after the fact.
- When an issue resolves: remove it from `pending-issues.md` and add a dated entry here.
- Every resolution gets an entry, including trivial ones. A trivial entry needs: symptom, when first noticed, what resolved it, and the date.
- If forum threads, bug reports, or upstream issues were found: include their URLs in the entry (confirms the issue is not machine-specific; reference point if it recurs or evolves upstream).

### notes/

| Belongs | Does not belong |
|---|---|
| How a subsystem works on this hardware | Reproduction steps (those go in `setup.md`) |
| Known platform limitations and their causes | Active workarounds (those go in `pending-issues.md`) |
| Context explaining why a config is the way it is | Per-issue narratives (those go in `debug-diary/`) |
| Sources: upstream docs, man pages, forums, issues, specs | |

- One file per topic; updated in place as understanding deepens.
- Record sources alongside facts: upstream docs, man pages, forum threads, GitHub issues, release notes.
- For hardware or system fact tables, add a `> **Note:**` after the table with a `| Purpose | Command |` table mapping each command to what it checks. One note covers the whole section; do not annotate individual rows.
- Update whenever investigation uncovers how a subsystem works, why a config decision was made, or what an upstream change means.
- If prompted by an issue or upgrade: reference the relevant `debug-diary/` or `pending-issues.md` entry at the top of the file.

### setup.md

- Update whenever a significant config change is made: a new service, a package upgrade that required intervention, or a config change with machine-specific implications.
- Splits into a set of topic-named files (e.g. `arch-install.md`, `dev-tools.md`, `extras-<topic>.md`) when a single file grows unwieldy or the installation naturally separates into stages; the partition `README.md` indexes them, the same way a project `README.md` indexes a folder it has outgrown.
- When a machine is retired: add a final `README.md` note with the retirement date and disposition.

### Research reference entry

```text
<project-notes>/pcs/<machine>/
└── README.md  # hardware summary, role, and code checkouts
```

The `README.md` covers:

- machine name and OS;
- a hardware summary table;
- the machine's role in the research workflow;
- a pointer to the setup repository;
- a `## Codes` table (code name, checkout path, role); no remote URLs, which belong in the codebase's own notes.
- update whenever checkout paths change or the machine's research role changes.
