# Documentation Style

These rules apply when writing or editing any markdown documentation: setup guides, design notes, lessons learned, and reference files.

---

## Characters

| Rule | |
|---|---|
| ASCII only | no Unicode punctuation: no em dashes, no curly quotes, no ellipsis characters |
| Dashes | use `-` for a dash; never `—` |
| Placeholders | use `<angle-brackets>`: `<package-name>`, `<username>`, `<commit-hash>` |

---

## Inline Formatting

| Rule | |
|---|---|
| Code, paths, commands, keys | always in backticks: `qalculate-gtk`, `~/.config/conky/conky.conf`, `Super+Ctrl+=` |
| Values and flags | backticks: `true`, `--offline`, `size=9` |
| Emphasis | use **bold** for warnings and key terms; avoid italic |
| Never inline commands | commands always go in a code block, never bare in prose |

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

- File locations and their purpose
- Sensor names, hardware details, component summaries
- Common tweaks (what to change and where)
- Structured comparisons

---

## Code Blocks

Every command goes in a code block. Never write a command inline in prose. Include the full command as it would be run — no ellipsis, no shorthand.

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

Document the reason behind non-obvious decisions, workarounds, and design choices. A reader should be able to understand not just what to do, but why it is done that way.

For setup guides, add a design decisions or lessons learned section where relevant. Cover:

- Why one approach was chosen over alternatives
- What broke and what fixed it
- Constraints that are not obvious from the config alone

---

## Examples

Examples should be generalised — no personal usernames, hostnames, or machine-specific paths unless the point of the example is machine-specific configuration. Use placeholders:

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
