# Writing: Documentation Style

Conventions for formatting, structuring, and writing Markdown documentation.

---

## Characters

| Rule | Detail |
|---|---|
| ASCII only | no Unicode punctuation: no em dashes, no curly quotes, no ellipsis characters |
| No em dashes or double hyphens | not in prose, not in tables, not as separators; `--` is not an acceptable substitute; use a comma, semicolon, or full stop instead |
| Not-applicable entries | write `N/A`, or let context show an entry is missing |
| File-organisation trees | inside fenced ```text blocks only, box-drawing characters (`├──`, `└──`, `│`, `─`) are permitted; ASCII everywhere else |
| Tree comments | `  # <comment>` with exactly two spaces between the entry and `#`; no column alignment |
| Placeholders | use `<angle-brackets>`: `<package-name>`, `<username>`, `<commit-hash>`; define each placeholder where it first appears, as a variable is defined when introduced in maths |

---

## Inline Formatting

| Rule | Detail |
|---|---|
| Code, paths, commands, keys | always in backticks: `<command>`, `~/.config/<app>/<file>`, `<Modifier>+<Key>` |
| Values and flags | backticks: `<bool>`, `--<flag>`, `<setting>=<value>` |
| Emphasis | use **bold** for warnings and key terms; avoid italic |
| Same-repo file | Markdown link: href is the real relative path to the file; display text is the path rooted at the repo's placeholder, e.g. `` [`<rules>/<path>/<file>.md`](../<path>/<file>.md) `` |
| Cross-repo file | plain backticks, no link; a relative href cannot resolve across git repos, e.g. `` `<project-notes>/<path>/<file>.md` `` |
| Directory or concept, not a specific file | plain backticks, no link, e.g. `` `<rules>/` `` |

---

## Math and Field Notation

| Rule | Detail |
|---|---|
| Scalars and vectors | lowercase letters; `f`, `g`. Where both appear together, use index notation to distinguish: `f_i` for vector components, `s` for scalars. |
| Greek quantities | spell out in words; `<greek>` |
| Code identifiers | exempt: source-code names keep their casing; `<CodeVar>` |
| Laplacian | `nabla^2 f` |
| Biharmonic | `nabla^4 f` |
| Higher powers | `nabla^N f` for any N |
| Divergence | `div(f)` |
| Curl | `curl(f)` |
| Gradient | `nabla s` |
| Cross product | `f x g` |
| Total derivative | `d_<i> <f>` |
| Partial derivative | `partial_<i> <f>` |
| Material derivative | `D_<i> <f>` |
| Subscripts | `_<subscript>` |
| Superscripts | `^<power>` |

---

## Equation Formatting

| Case | Format |
|---|---|
| Simple definition or short expression | inline backtick |
| Equation that carries significance | fenced code block |

---

## Structure

| Rule | Detail |
|---|---|
| Section separators | `---` between top-level sections |
| Headings | `##` for top-level sections, `###` for subsections |
| No trailing period on headings | |
| Bold sub-labels | `**Label:**` to group related tables within a section when a `###` heading is too heavy |
| Numbered lists | for sequential steps or ordered rules where position carries meaning |
| Bullet lists | for unordered items |
| Table column names | every column must have a name; an unnamed column is a sign the table should be a bullet list |

---

## Choosing a form

Content grows over time, so it lives in the lightest form that holds it now and is promoted up a ladder as it outgrows that form. Each rung is extended by slotting in a unit, never by rewriting:

| Rung | Use when | Grow by |
|---|---|---|
| Bullet list | A few standalone concepts that share no columns | Adding bullets |
| Table | Items share two or more real columns: a mapping, a comparison, or a label-to-definition lookup | Adding rows |
| Subsection with a table or bullets | One concept grows rich enough to need its own heading and internal structure | Adding subsections |
| Sub-file | A section outgrows the file or spans domains (see [`workflow/note-taking/project.md`](../workflow/note-taking/project.md)) | Adding files |

Promote when the current rung strains:

- A bullet that keeps gaining the same repeated field wants to be a table.
- A table cell that turns dense wants to be a subsection.
- A subsection that turns large wants to be its own file.

A table earns its place only with two or more columns that each carry the same kind of value in every row. To test a would-be table, name the second column: if it has one consistent name and value-kind per row it is a table; if the only honest name is "Notes", the cells differ in kind and it is still a bullet list.

Prose is the one form off the ladder: it cannot be extended or reorganised without rewriting. Reserve it for the **why** behind a rule or the **philosophy** of a concept (see [Capturing the Why](#capturing-the-why)), never for a set of rules.

---

## Code Blocks

Runnable commands and copy-paste instructions are written in code blocks, not inline prose. Inline code remains appropriate for naming a command, script, path, module, key, or flag when the reader is not being asked to run it. Runnable commands are shown in full, as they would actually be entered, with no ellipsis or shorthand. Do not add inline comments that contain conditions or guidance requiring a decision; express those as prose before or between blocks.

---

## Caveats and Notes

Use `>` blockquotes for:

- Caveats that apply to the section
- Known issues or workarounds that may need revisiting
- Behaviour the reader might not expect

Example:

> **Note:** this workaround should be revisited after upstream resolves the issue.

---

## Capturing the Why

Document the reason behind non-obvious decisions, workarounds, and design choices. A reader should understand not just what to do, but why.

Prose earns its place in only two cases:

- the **why** behind a non-obvious rule;
- the **philosophy** of a concept where the rule alone would feel arbitrary.

Write it as statements of fact, not instructions, and cut any sentence that only restates a rule belonging in a table or list.

For setup guides, add a design decisions or lessons learned section where relevant. Cover:

- Why one approach was chosen over alternatives
- What broke and what fixed it
- Constraints that are not obvious from the config alone

---

## Prose Style

| Rule | Detail |
|---|---|
| Short and direct | no filler words or throat-clearing |
| Active voice | prefer "run this command" over "this command should be run" |
| Present tense | prefer "this fixes" over "this will fix" |
| No personal references | write for a general reader, not yourself |
| No manual line wrapping | prose flows to the editor's window width; do not insert line breaks within paragraphs. Does not apply to structured fields where each line is a distinct labeled item (e.g. `**Status:** ...` / `**Next action:** ...` blocks). |

---

## Anonymous Examples

Examples should illustrate the concept, not a specific instance. Use `<angle-bracket>` placeholders instead of real names, paths, or values. This applies to inline examples and code blocks alike.

| Rule | Detail |
|---|---|
| No personal names | no real usernames, hostnames, or email addresses |
| No machine-specific paths | use `~/.config/<app>/<file>`, not `~/.config/conky/conky.conf` |
| No real package names as examples | use `<package-name>`, not a specific package |
| Exception | when the example **is** the specific thing being documented (e.g. the exact command to install a particular app) |
