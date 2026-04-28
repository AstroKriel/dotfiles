# Documentation Style

These rules apply when writing or editing any markdown documentation: setup guides, design notes, lessons learned, and reference files.

---

## Characters

| Rule | |
|---|---|
| ASCII only | no Unicode punctuation: no em dashes, no curly quotes, no ellipsis characters |
| No em dashes as punctuation | use a comma, semicolon, or full stop instead; never use `—` to set off a clause |
| Placeholders | use `<angle-brackets>`: `<package-name>`, `<username>`, `<commit-hash>` |

---

## Inline Formatting

| Rule | |
|---|---|
| Code, paths, commands, keys | always in backticks: `<command>`, `~/.config/<app>/<file>`, `<Modifier>+<Key>` |
| Values and flags | backticks: `<bool>`, `--<flag>`, `<setting>=<value>` |
| Emphasis | use **bold** for warnings and key terms; avoid italic |
| Runnable instructions | commands the reader is expected to run belong in a code block, not inline prose |

---

## Structure

| Rule | |
|---|---|
| Section separators | `---` between top-level sections |
| Headings | `##` for top-level sections, `###` for subsections |
| No trailing period on headings | |
| Numbered lists | for sequential steps where order matters |
| Bullet lists | for unordered items |

---

## Tables

Use tables for:

- Rules and conventions
- File locations and their purpose
- Sensor names, hardware details, component summaries
- Common tweaks (what to change and where)
- Structured comparisons

---

## Code Blocks

Runnable commands and copy-paste instructions are written in code blocks, not inline prose. Inline code remains appropriate for naming a command, script, path, module, key, or flag when the reader is not being asked to run it. Runnable commands are shown in full, as they would actually be entered, with no ellipsis or shorthand.

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

Rules belong in tables. Prose is for two cases: explaining the **why** behind a non-obvious rule, and capturing the **philosophy** behind a concept where the rule alone would feel arbitrary. Both are written as statements of fact, not instructions; if prose is restating a table rule, cut it.

For setup guides, add a design decisions or lessons learned section where relevant. Cover:

- Why one approach was chosen over alternatives
- What broke and what fixed it
- Constraints that are not obvious from the config alone

---

## Examples

Examples should illustrate the concept, not a specific instance. Use `<angle-bracket>` placeholders instead of real names, paths, or values. This applies to inline examples and code blocks alike.

| Rule | |
|---|---|
| No personal names | no real usernames, hostnames, or email addresses |
| No machine-specific paths | use `~/.config/<app>/<file>`, not `~/.config/conky/conky.conf` |
| No real package names as examples | use `<package-name>`, not a specific package |
| Exception | when the example IS the specific thing being documented (e.g. the exact command to install a particular app) |

```bash
git clone https://github.com/<username>/<repo>.git
```

Not:

```bash
git clone https://github.com/myusername/myrepo.git
```

---

## Prose Style

| Rule | |
|---|---|
| Short and direct | no filler words or throat-clearing |
| Active voice | prefer "run this command" over "this command should be run" |
| Present tense | prefer "this fixes" over "this will fix" |
| No personal references | write for a general reader, not yourself |
