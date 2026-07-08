# Git: Pull Request Titles

Conventions for writing pull request titles.

## Format

PR titles become the squash-merge commit subject. They appear in `git log --oneline`, `git blame`, and side-by-side diff views, so they are the durable subject line for a change.

```
Action: short detail
```

PR titles diverge from [commit message style](commits.md) in three ways: sentence case (not lowercase), no trailing period, and no `(scope)` parens. The reason is rendering context: commit messages live mostly in `git log` (terse); PR titles also appear in GitHub lists and release notes where sentence case reads better.

| Rule | Detail |
|---|---|
| Case | sentence case: first word capitalised; rest follows normal sentence rules |
| Voice | imperative present: `Add`, `Fix`, `Update`, never `Adds` or `Added` |
| Action vocabulary | same set as [commits](commits.md), expanded when an abbreviation reads awkwardly: `del` -> `Remove`, `config` -> `Configure`, `docs` -> `Document` |
| Separator | `:` after the action; right side stays lowercase as continuation |
| Multiple clauses | `;` between clauses; right clause stays lowercase |
| Ending | no trailing period |
| Length | target under 72 characters; hard cap 100 |
| Scope | omit `(scope)` parens; the diff and PR description carry that |

## Examples

```
Add <feature>: <one-line description>
Fix <component>: <what broke and how it is fixed>
Refactor <module>: <structural change>
Update <thing>: <what changed>
Rename <dir>/: <naming change>
Document <topic>: <what is documented>
```
