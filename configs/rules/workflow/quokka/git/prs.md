# Quokka: Pull Requests

How to open and describe pull requests against the Quokka `development` branch.

> **Note:** open a PR only after completing the branch review in [`workflow/git/review-branch.md`](../../git/review-branch.md) and confirming local tests pass.

---

## Title

Follow the PR title rules in [`workflow/git/pull-requests.md`](../../git/pull-requests.md): sentence case, imperative, no trailing period, under 72 characters.

```
Action <Component>: short detail
```

The title becomes the squashed commit message on merge, so it must be specific enough to stand alone in `git log`.

---

## Structure

The GitHub PR template provides three sections, always present:

| Section | Role |
|---|---|
| `### Description` | What changed, why, and the reasoning behind design choices. |
| `### Related issues` | Links to the proposal this PR implements and any it enables. |
| `### Checklist` | Repo compliance items; includes the GPU test trigger. |

Add situational `### ` sections after `### Description`, as they apply. Each is a top-level `### ` section, not a bold sub-header inside `### Description`:

| Section | When to use |
|---|---|
| `### Validation` | convergence results or analytic comparisons confirming correct behaviour |
| `### Energy conservation` | tests confirming energy is transferred correctly between components |
| `### Known issues` | `[Feedback]`/`[Testing]` PRs: items that must be resolved before the PR is ready for review |
| `### Request for Feedback` | `[Feedback]` PRs: specific questions on the approach you want reviewers to weigh in on |

---

## Description

- Write in first person.
- Cover what changed, why, and the reasoning behind any non-obvious design choices: what you tried, what you found, and what tradeoffs you made.
- Reviewers benefit from understanding the judgment, not just the outcome.

- Keep `### Description` to prose; break supporting material out into the situational `### ` sections listed under [Structure](#structure) (`### Validation`, `### Known issues`, etc.) rather than bold sub-headers within the description.
- Wherever a test result is cited, include a figure; the caption or surrounding prose must state the test name, any non-default parameters, and the resolution used.
- Equations follow the notation rules in [`writing/markdown.md`](../../../writing/markdown.md).

---

## Title status tags

While the PR is a draft, prefix the title with a stage tag to communicate progress on top of GitHub's own draft/ready toggle. Every tagged stage is a draft:

| Tag | Meaning |
|---|---|
| `[WIP]` | still implementing; not yet shareable, even for early feedback |
| `[Feedback]` | shareable draft; seeking feedback on the approach before continuing |
| `[Testing]` | implementation is believed complete; running tests, tweaks may be called for based on tests |

- Ready for review is the untagged state: when all known issues are resolved and CI is green, remove the stage tag entirely and flip the PR from draft to ready for review. A title with no tag is the signal that the code is ready to read.
- Because the ready-for-review title already carries no tag, it doubles as the clean squashed commit message; no stage marker leaks into `git log`.

---

## Related issues

- Link the discussion or issue this PR implements and any discussions or issues this PR unblocks or enables.
- Explain the relationship in one sentence each.

```
- #<N>: this PR implements the proposal.
- #<M>: this PR is a prerequisite; <brief reason why>.
```

---

## Checklist

The repo template checklist:

- [ ] I have added a description (see above).
- [ ] I have added a link to any related issues (if applicable; see above).
- [ ] I have read the [Contributing Guide](https://github.com/quokka-astro/quokka/blob/development/CONTRIBUTING.md).
- [ ] I have added tests for any new physics that this PR adds to the code.
- [ ] *(For quokka-astro org members)* I have manually triggered the GPU tests with the magic comment `/azp run`.

- The tests item applies when the PR adds a new physical process; not to infrastructure or harness changes.
- After opening the PR, post `/azp run` as a comment to trigger the GPU test pipeline.
