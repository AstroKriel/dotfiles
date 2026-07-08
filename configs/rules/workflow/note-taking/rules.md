# Notes: Rules

How to use, add to, and extend the `~/.rules/` system.

---

## What it is

The canonical source is `<system-configs>/configs/rules/`. All `.md` files there are symlinked into `~/.rules/` (written `<rules>/` in cross-references throughout these files) by `uv run -m scripts.setup.rules_files` run from the SystemConfigs repo. Edit the source; never edit through a symlink. The one exception is the generated `README.md` index: `rules_index` writes it directly into `~/.rules/`, so it is a regular file, not a symlink.

---

## Structure

```text
<rules>/
├── code/  # conventions for producing code and scripts
│   ├── python/  # Python language bundle
│   └── quokka/  # Quokka project bundle
├── writing/  # conventions for producing text
└── workflow/  # conventions for how to work
    └── note-taking/  # this bundle
```

---

## What belongs here

A rule belongs in `<rules>/` when it is a binding convention: it applies across future uses of a tool, language, or context, and it prescribes how to do something.

| Belongs in `<rules>/` | Does not belong |
|---|---|
| How to write a docstring | What a specific function does |
| Commit message format | Status of an ongoing investigation |
| Agent collaboration modes | HPC machine hardware specs |
| File and folder naming conventions | Lessons learned from a specific simulation run |
| Which tool or library to use and the non-obvious constraints | API documentation: which function to call, which arguments to pass; read the library instead |

When in doubt: a rule answers "what is the convention?" A note answers "what is known?". See `README.md` in this bundle for the full decision rubric.

---

## Adding a rule

1. Find the right file. Read [`<rules>/README.md`](../../README.md) for the full index. Use an existing file if the topic fits; create a new one if nothing covers it.
2. Edit the source under `<system-configs>/configs/rules/`.
3. From `<system-configs>/`, run `uv run -m scripts.setup.rules_files` to relink and `uv run -m scripts.setup.rules_index` to regenerate the index.
4. Commit following [`workflow/git/commits.md`](../git/commits.md).

**New file:**
- name it `<concept>.md`; one word or a short phrase naming the subject
- open with a title, then a single present-tense sentence describing what the file covers; no second sentence or cross-references
- title format: `<Bundle>: <Concept>` -- gives domain and topic in full so the file is self-describing without reference to its path; the description sentence narrows scope further
- that sentence becomes the index entry

**Promoting a file to a bundle:**
- when a single file grows to cover sub-topics that each warrant their own section, convert it to a subdirectory
- create a `README.md` inside for any context that applies to the bundle as a whole
- split content into per-topic files

**New bundle:**
- when the concept is large from the start, create the subdirectory directly
- add a `README.md` if there is bundle-level context to capture
- follow the existing bundle pattern in `code/python/` or `code/quokka/`
---

## Promoting a finding

A finding in the notes system becomes a rule when it represents a stable convention you would apply again in future work, not just to the instance that produced it. Phrase it prescriptively, but do not force it into a binary: a convention that applies in most contexts is still worth capturing.

To promote:

1. Identify which `<rules>/` file the convention belongs in.
2. Phrase it as a rule: prescriptive, not descriptive.
3. In the notes source, note the promotion if the investigation entry is still live; the rule itself carries no back-reference.
4. Commit following [`workflow/git/commits.md`](../git/commits.md).
