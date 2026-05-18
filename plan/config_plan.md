# Config Plan Resolver Behaviour Spec

Companion to `overview.md` and `config_registry.md`. This is a TDD target:
every `*-N` behaviour below is one acceptance criterion, which is at least one
unit test. A reference such as `ov#5` points at an `overview.md` numbered
decision.

---

## Tension

The resolver is the densest logic in the pipeline and the artefact every later
stage trusts. It is correct only if it is pure: the host is an injected
`system_descriptor`, never probed. Purity is what lets the
profile-by-platform golden matrix run with no real machine, so this spec pins
the resolver behaviour before any code exists.

---

## Scope

This spec covers only `resolve_config`, the pure stage that turns a filtered
config registry into a `config_plan`.

In scope: avenue selection and precedence, dependency ordering, manager
bootstrap insertion, choice-group teardown materialisation, step emission, the
hard-stop semantics, and determinism.

Out of scope, handed elsewhere: host detection (`detect_system`, impure;
`resolve_config` only consumes its `system_descriptor` output); discovery and
filtering (`config_registry.md`); side effects, idempotence, and `--bootstrap`
policy (`executor.md`). `resolve_config` performs no I/O and reads nothing from
the host.

---

## Inputs and artefact

| Name | Origin | Role |
|---|---|---|
| `filtered_config_registry` | `config_registry.md` | subscribed concepts plus concept `needs`-closure, relationships intact |
| `system_descriptor` | `detect_system` (injected) | platform tags, present managers; the detected fact |
| `resolve_policy` | profile plus capability map | `prefer_managers`, `exclude_managers`, the global default ranking (ov#16), `platform -> [managers]` |

Result: `config_plan` or an aggregated `ResolutionError`. `resolve_config` is a
pure function of these three inputs.

---

## Avenue selection, AVN

| ID | Behaviour | Failure |
|---|---|---|
| AVN-1 | The chosen avenue follows the ov#5 ladder: capability (managers present, intersected with platform candidates), then the config-spec set as binding, then `prefer_managers`, then config-spec order, then the global default ranking. | n/a |
| AVN-2 | `exclude_managers` removes avenues before selection (ov#13). | n/a |
| AVN-3 | `prefer_managers` only reorders avenues whose manager is present; it is inert when its target is absent (ov#13). | n/a |
| AVN-4 | A `when.platform` not in the descriptor's platform tags excludes that avenue or link (ov#8). | n/a |
| AVN-5 | If a subscribed concept has no surviving avenue, that is a hard-stop cause (ov#3, ov#8). | `ResolutionError` cause |
| AVN-6 | One-avenue and `kind = "script"` cases are non-negotiable: the set has size one, so policy cannot reorder it. | n/a |

---

## Dependency resolution, DEP

`filtered_config_registry` already holds the concept `needs`-closure;
bare-package `needs` are recorded raw (`config_registry.md` FIL-3). This stage
orders and emits, it does not re-classify.

| ID | Behaviour | Failure |
|---|---|---|
| DEP-1 | Resolution order is topological: a concept's `needs` are ordered before the concept (ov#11). | n/a |
| DEP-2 | A bare-package `needs` emits an `install` step before the dependent concept's `install`. | n/a |
| DEP-3 | A concept `needs` (already in the filtered set) is ordered before its dependent and contributes its own steps once. | n/a |
| DEP-4 | A dependency cycle is a hard-stop cause, not an infinite loop (ov#11). | `ResolutionError` cause |

---

## Manager resolution, MGR

| ID | Behaviour | Failure |
|---|---|---|
| MGR-1 | The chosen avenue's manager must be present or bootstrappable. | n/a |
| MGR-2 | Manager absent and subscribed (`managers = [...]`): a manager-bootstrap step is inserted before any concept whose avenue needs it (ov#14). | n/a |
| MGR-3 | Manager absent and not subscribed: hard-stop cause; a manager is never installed silently (ov#14). | `ResolutionError` cause |
| MGR-4 | Base managers (`pacman`, `dnf`, `apt`) are assumed present; no bootstrap step is emitted. | n/a |
| MGR-5 | A bootstrap that itself needs a base manager (yay via pacman) is ordinary topological order (DEP-1). | n/a |
| MGR-6 | Idempotence (`[check]`) is the executor's concern; `resolve_config` still emits the bootstrap step unconditionally. | n/a |

---

## Choice-group teardown, GRP

| ID | Behaviour | Failure |
|---|---|---|
| GRP-1 | `ChoiceGroupError` is raised upstream at filter time (`config_registry.md` FIL-4); `resolve_config` assumes a valid filtered set. | n/a |
| GRP-2 | A recorded `_teardown` sibling becomes a `teardown` step, emitted after the kept member's steps (ov#6, ov#15). | n/a |
| GRP-3 | Teardown is derived from the kept and recorded set, never declared in a config spec. | n/a |

---

## config_plan shape and emission, PLN

| ID | Behaviour | Failure |
|---|---|---|
| PLN-1 | Step kinds are `install`, `render`, `link`, `copy`, `post-hook`, `teardown`. `check` is a gate, not a step (ov#6). | n/a |
| PLN-2 | Within one concept the step order is `install`, then `render`, then `link` or `copy`, then `post-hook`. | n/a |
| PLN-3 | Global order: managers and dependencies before dependents (DEP-1, MGR-2); group teardown after the kept member. | n/a |
| PLN-4 | `config_plan` serialises as JSON with sorted keys; the same inputs yield byte-identical output (ov#18). | n/a |
| PLN-5 | `resolve_config` is pure: no host access, no I/O; injectable; a prebuilt `config_plan` may be passed downstream instead. | n/a |
| PLN-6 | Every hard-stop cause is collected and reported together; there is no partial `config_plan` (ov#4). | `ResolutionError` |

---

## Examples

Each example is the literal test fixture and its expected value, so the
example is the acceptance test, not a separate illustration.

AVN-1, avenue selection (same `fd` config spec as `overview.md`):

```text
avenues          : [brew, pacman, cargo]
detected present : [pacman, cargo]            # brew absent
policy           : prefer_managers = ["cargo"]

-> brew removed (absent); set [pacman, cargo]; prefer orders cargo first
-> chosen avenue cargo; step { action: install, pkg: "fd-find" }
```

DEP-1 and DEP-2, bare-package ordering:

```text
conky needs ["lua"]   # "lua" not a concept key -> bare package

steps = [
  { action: install, pkg: "lua" },
  { action: install, concept: "conky" },
  { action: link,    concept: "conky" },
]
```

MGR-2 and MGR-3, bootstrap versus hard-stop:

```text
fresh macOS; tmux avenue is brew-only; brew absent

managers = ["brew"]  -> [ bootstrap brew, install tmux, link tmux ]
managers = []        -> ResolutionError: tmux needs brew; absent and not subscribed
```

GRP-2, teardown materialisation:

```text
shell-bash, shell-zsh both group = "shell"; subscribe [shell-zsh]

steps = [
  { action: install,  concept: "shell-zsh" },
  { action: link,     concept: "shell-zsh" },
  { action: teardown, concept: "shell-bash" },
]
```

PLN-6, aggregated hard-stop:

```text
zathura subscribed on linux (macOS-only avenue)
qux subscribed; only avenue needs manager "nix", absent and not subscribed

-> ResolutionError [
     "zathura: only available on [macos]",
     "qux: needs nix; absent and not subscribed",
   ]
   no config_plan produced
```

---

## Errors

`ResolutionError` is a single aggregated error carrying every cause found, in
keeping with the plan-first accountability of ov#4.

| Cause | Raised by |
|---|---|
| no surviving avenue | AVN-5 |
| platform-unavailable | AVN-4 leading to AVN-5 |
| manager absent and unsubscribed | MGR-3 |
| dependency cycle | DEP-4 |

---

## Test obligations

| Obligation | Detail |
|---|---|
| Golden plans | `config_plan` over the fixture tree, by each of the four `config-profiles/*.toml`, by a set of synthetic `system_descriptor` fixtures |
| Descriptor matrix | per profile: ideal (all candidate managers present); manager absent and subscribed (expect bootstrap step); manager absent and unsubscribed (expect `ResolutionError`); wrong platform (expect `ResolutionError`) |
| Hard-stop | cycle, no-avenue, and multi-cause cases assert an aggregated `ResolutionError` and zero plan output |
| Properties | `load(dump(x)) == x`; identical inputs yield identical bytes; resolution is order-independent in inputs |
| Isolation | no test touches the real `$HOME` or probes the host; the `system_descriptor` is always constructed by hand |

---

## Handoff to executor.md (not yet written)

`execute_config(config_plan)` owns: side effects via `apply_shell_actions`,
idempotence through `[check]`, render written into the tracked `configs/` tree
and committed (ov#6), `link` versus `copy`, `teardown` link removal, and
running install commands or `install.sh`. The `--bootstrap` run-versus-print
policy is still open (`overview.md` "Still open"); the lean is print-only by
default, execute opt-in per platform.
