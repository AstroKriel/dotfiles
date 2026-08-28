# Asgard: Science Project

How to start, run, and archive science projects in the Asgard ecosystem.

---

## Starting a New mimir Project

Start a new mimir project once the core idea is solid and prototyping in `freyja` has validated the approach.

Sequence:

1. Create the repo following the naming conventions in the Publication and Archival section below
2. Register it as a git submodule under `Asgard/mimir/`
3. Initialise a uv project and configure `pyproject.toml` per [`<rules>/code/python/setup-project.md`](../../code/python/setup-project.md)
4. Add `jormi` and any relevant `ww-*-sims` packages as editable dependencies
5. Open a notes directory: `<project-notes>/<project>/` with `README.md`
6. Push to GitHub

### Initial structure

```text
<project>/
├── pyproject.toml
├── README.md
├── src/
│   └── <package>/
│       └── __init__.py
└── scripts/
```

`scripts/` holds entry-point scripts: analysis, figure generation, data pipeline steps. `src/<package>/` holds reusable library logic. Keep the two layers separate from the start.

---

## Data Placement

Choose where data or scratch work goes based on its scope and intended lifespan:

| Location | Lifespan | Use when |
|---|---|---|
| `/tmp/` | reboot-ephemeral | shell pipes, one-shot outputs; fine to lose on reboot |
| `~/tmp/` | indefinite | personal operational scratch; survives reboots but has no project or scientific home |
| `freyja` | until formalised | prototyping with intent to open a mimir project |
| `<project>/<category>/dev/` | project lifetime | data belonging to an active mimir project |

### Project dev: `<category>/dev/`

Untracked, in-development data for an active project lives under a `dev/` subfolder inside each relevant top-level category, not at the project root:

```text
<project>/
├── datasets/
│   └── dev/   # untracked
├── figures/
│   └── dev/   # untracked
└── scripts/
    └── dev/   # tracked; work-in-progress scripts, not data
```

- Add `datasets/dev/` and `figures/dev/` to the project's `.gitignore`; `scripts/dev/` stays tracked since it holds code, not data.
- Name subfolders inside a `dev/` directly for what they contain (a dataset name, a diagnostic being developed, etc.) -- no further nesting convention required.

### Scratch folder structure: `/tmp/` and `~/tmp/`

Both `/tmp/` and `~/tmp/` group items by a concept folder. Inside it, leaf items get a `<YYYY-MM-DD>-<description>` prefix:

```text
~/tmp/
└── <concept>/
    └── <YYYY-MM-DD>-<description>
```

For `/tmp/`, add a user namespace first: `/tmp/<username>/<concept>/`.

**Naming the concept folder:** ask "what is this work about?" The answer, slugified, is the concept name. If the answer is a named entity in the Asgard ecosystem (a tool or a mimir project), use its canonical slug. If the answer is an activity with no canonical name, coin a short lowercase descriptor. Named entities take priority over descriptors.

- Review and prune `~/tmp/` by concept every three months.

---

## Publication and Archival

When a paper is accepted:

1. Rename the repo following the naming conventions below
2. Update the GitHub repository name and any local refs pointing to it
3. Tag the accepted-version commit: `git tag accepted`
4. Pin `jormi` and any `ww-*-sims` dependencies to git commits -- see [`<rules>/code/asgard.md`](../../code/asgard.md)
5. Make no further changes after renaming
6. Add a final log entry to `<project-notes>/<project>/log/` with the journal and acceptance date

The local folder name and the GitHub repository name follow different conventions:

| Location | Format | Example |
|---|---|---|
| Local folder | `<author1>[-<author2>]-<year>-<title-identifiers>` | `<author1>-<author2>-2025-<title>` |
| GitHub | `<Author1>[<Author2>]<year>_<title-identifiers>` | `<Author1><Author2>2025_<title>` |

For two or three authors, include all names; for more, use only the first author's name.

Precision promotion is not the responsibility of project code in `mimir`; it belongs in `jormi`. See [`<rules>/code/asgard.md`](../../code/asgard.md) for the data representation rule.
