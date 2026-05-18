# Config Registry Pipeline Behaviour Spec

Companion to `overview.md`. This is a TDD target: every `*-N` behaviour below
is one acceptance criterion, which is at least one unit test. A reference such
as `ov#3` points at an `overview.md` numbered decision.

---

## Tension

The pipeline cannot be tested as a whole until its stages are separable. The
config-registry stages are the two that need no host, so they are pinned first
and in isolation; everything host-dependent is deferred so these stages stay
pure and machine-free.

---

## Scope

This spec covers only the two config-registry artefacts:

- stage 1, discover, producing `full_config_registry`
- the subscription filter, producing `filtered_config_registry`

Out of scope, handed to a future `resolve.md` and `executor.md`: host
detection (`system_descriptor`), avenue and manager selection, platform
availability hard-stop, `needs` topological ordering, manager-bootstrap
insertion, render, execute, teardown materialisation. Where avenues and links
appear here the concern is structural only (the set exists and parses), never
which one runs on a given machine.

---

## Artefacts

| Artefact | Shape | Pure function of | Serialised | Tracked |
|---|---|---|---|---|
| `full_config_registry` | keyed map `concept_key -> ConfigSpec`, relationships intact | the `configs/` tree | JSON, sorted keys | yes, lock-style; a PR diff shows config-spec changes |
| `filtered_config_registry` | same shape, restricted to subscriptions plus concept `needs`-closure | `full_config_registry` plus profile | JSON, sorted keys | no; depends on profile |

Both are injectable: by default each recomputes; a prebuilt artefact may be
passed in instead, for tests, accountability, or speed.

Serialised shapes over a two-concept fixture (`tmux`, `conky`), profile
subscribing `tmux` only:

```json
// full_config_registry.json
{
  "conky": { "group": null, "needs": ["lua"], "links": ["conky.conf"] },
  "tmux":  { "group": null, "needs": [],      "links": ["tmux.conf"] }
}
```

```json
// filtered_config_registry.json
{
  "tmux": { "group": null, "needs": [], "links": ["tmux.conf"] }
}
```

Keys are sorted; `filtered_config_registry` is a strict subset with
relationships intact. These literal files are the golden-test fixtures, not
illustrations.

---

## Config-spec parse, SPEC

| ID | Behaviour | Failure |
|---|---|---|
| SPEC-1 | A concept directory must contain `_config_spec.toml` (ov#1). | `ConfigSpecMissingError(path)` |
| SPEC-2 | Required: `name` (non-empty string), at least one `[[install]]`. Optional: `[check]`, 0..N `[[link]]`, `group`, `needs`. | `ConfigSpecSchemaError` |
| SPEC-3 | `[[install]].kind`: omitted means package and requires `pkg`; `config-only` forbids `pkg`; `script` forbids `pkg` and implies an `install.sh` sibling. | `ConfigSpecSchemaError` |
| SPEC-4 | `when` keys are a subset of `{platform, manager}` only (ov#10). | `ConfigSpecSchemaError` |
| SPEC-5 | `[[link]]`: `source` (a filename or `"."`), `dir`, `name`, `mode` in `{link, copy}`. | `ConfigSpecSchemaError` |
| SPEC-6 | `group` is an optional string, defining choice-group membership (ov#15). | n/a |
| SPEC-7 | `needs` is a list of strings, kept raw; the concept-versus-package distinction is resolved later. | n/a |
| SPEC-8 | Parsing is pure and total: it returns a `ConfigSpec` or a typed error carrying `(path, reason)`, never an untyped exception, and reads nothing outside the given file. | typed error |

---

## Discover, FUL

| ID | Behaviour | Failure |
|---|---|---|
| FUL-1 | Discovery scans `configs/<group>/<concept>/_config_spec.toml`. The group set is explicit (`tools, editors, shell, extras, managers, rules`), never inferred. | n/a |
| FUL-2 | `concept_key` is unique across all groups. | `ConfigRegistryError(duplicate key, paths)` |
| FUL-3 | `full_config_registry` is a pure deterministic function of the tree: the same tree yields byte-identical serialisation. | n/a |
| FUL-4 | Relationships are first-class and preserved: `needs` edges and `group` membership are recorded, not flattened. This is the synergy-between-related-concepts requirement. | n/a |
| FUL-5 | An unknown `needs` target is not an error here; it may be a bare package. The config registry records; cross-concept validation is deferred to resolve. | n/a |
| FUL-6 | One malformed config spec fails the whole build with the offending path; no partial config registry (ov#4). | propagated typed error |
| FUL-7 | Serialisation round-trips: `load(dump(r)) == r`; keys sorted; a prebuilt `full_config_registry` skips the scan. | n/a |

---

## Filter, FIL

| ID | Behaviour | Failure |
|---|---|---|
| FIL-1 | Input is `full_config_registry` plus the parsed profile (subscription lists `tools, editors, extras, shell, managers`). | n/a |
| FIL-2 | Every subscribed key must exist in `full_config_registry`; all unknowns are reported (ov#3). | `SubscriptionError(unknowns)` |
| FIL-3 | Result is the subscribed keys plus their `needs`-closure that are themselves concepts (recurse); bare-package `needs` are recorded, not pulled in (ov#11). | n/a |
| FIL-4 | At most one subscribed concept per `group`. Unsubscribed siblings of a subscribed group member are recorded for derived teardown (ov#6, ov#15). | `ChoiceGroupError(group, members)` |
| FIL-5 | Same structure and relationships as `full_config_registry`: a subset, not a flattening. | n/a |
| FIL-6 | Pure and deterministic given `(full_config_registry, profile)`; serialisable; injectable. | n/a |
| FIL-7 | Filtering consults no host state. It raises only the host-free errors `SubscriptionError` and `ChoiceGroupError`; platform and manager availability hard-stops belong to resolve. | n/a |

---

## Examples

Each example is written as the literal test fixture and its expected value, so
the example is the acceptance test, not a separate illustration.

SPEC-3, the `kind` and `pkg` legality matrix:

| `kind` | `pkg` present | Result |
|---|---|---|
| omitted | yes | valid (package install) |
| omitted | no | `ConfigSpecSchemaError` |
| `config-only` | no | valid |
| `config-only` | yes | `ConfigSpecSchemaError` |
| `script` | no | valid (expects `install.sh`) |
| `script` | yes | `ConfigSpecSchemaError` |

SPEC-4, an illegal `when` key:

```toml
[[install]]
when = { platform = "macos", arch = "arm64" }   # `arch` not in {platform, manager}
```

```text
-> ConfigSpecSchemaError(path, "unknown when key: arch")
```

FUL-2, a duplicate concept key across groups:

```text
configs/tools/fd/_config_spec.toml
configs/extras/fd/_config_spec.toml
-> ConfigRegistryError("duplicate concept key: fd", [tools/fd, extras/fd])
```

FUL-5, an unknown `needs` target is recorded, not rejected:

```text
conky needs ["lua"]; no "lua" key in the tree
-> full_config_registry builds successfully; "lua" recorded raw on conky
```

FIL-3, the `needs`-closure with the bare-package split:

```text
full_config_registry keys : { conky, zathura }     # no "lua" key
profile subscribes        : [conky]
conky needs               : ["lua", "zathura"]

"lua"     not a key -> bare package -> recorded, not added to membership
"zathura" is a key  -> concept      -> added to filtered_config_registry (recurse)

filtered_config_registry membership = { conky, zathura }
```

FIL-4, the choice group, inputs and expected error:

```text
shell-bash, shell-zsh both carry group = "shell"

subscribe [shell-bash, shell-zsh]
  -> ChoiceGroupError(group="shell", members=["shell-bash","shell-zsh"])

subscribe [shell-zsh]
  -> ok; shell-bash recorded for derived teardown
```

Error aggregation, two faults in one input, both reported:

```text
configs/tools/a/   missing _config_spec.toml
configs/tools/b/_config_spec.toml   has when = { os = "linux" }

-> [ ConfigSpecMissingError(tools/a),
     ConfigSpecSchemaError(tools/b, "unknown when key: os") ]
```

---

## Errors

All errors are typed, actionable, and aggregated: the build reports every
failure it can find before exiting, never stopping at the first. This matches
the plan-first accountability of ov#4.

| Error | Raised by |
|---|---|
| `ConfigSpecMissingError` | SPEC-1 |
| `ConfigSpecSchemaError` | SPEC-2 to SPEC-5 |
| `ConfigRegistryError` | FUL-2 (duplicate key) |
| `SubscriptionError` | FIL-2 |
| `ChoiceGroupError` | FIL-4 |

---

## Test obligations

| Obligation | Detail |
|---|---|
| Fixture trees | one valid `configs/` tree, plus one per malformed variant: missing config spec, bad `kind`, illegal `when` key, missing link field, duplicate key |
| Coverage | at least one test per SPEC, FUL, FIL id |
| Golden serialisation | `full_config_registry` and `filtered_config_registry` over the fixture tree, by each of the four `config-profiles/*.toml` |
| Properties | `load(dump(x)) == x`; identical tree yields identical bytes; filtering is idempotent |
| Isolation | no test in this spec touches the real `$HOME` or probes the host; a behaviour needing that belongs in `resolve.md` |

---

## Handoff to resolve.md (not yet written)

`resolve_config(filtered_config_registry, system_descriptor, policy) ->
config_plan or ResolutionError` owns: detection, avenue and manager selection
(ov#5), platform availability hard-stop (ov#3, ov#8), manager bootstrap
(ov#14), `needs` topological order (ov#11), choice-group teardown
materialisation, and render, link, and post-hook step emission.
