# Registry Pipeline — Behaviour Spec

Companion to `overview.md`. This is a **TDD target**: every `*-N` behaviour
below is one acceptance criterion = at least one unit test. Decision refs like
`(ov#3)` point at `overview.md` numbered decisions.

## Scope

Covers **only** the two registry artefacts:

- **stage 1 — discover** → `full_registry`
- **subscription filter** → `filtered_registry`

Explicitly **out of scope** (handed to a future `resolve.md` / `executor.md`):
host detection (`SystemDescriptor`), avenue/manager *selection*, platform
availability hard-stop, `needs` topo-ordering, manager-bootstrap insertion,
render, execute, teardown materialisation. Where avenues/links are mentioned
here it is **structural only** (the set exists and parses) — never "which one
runs on this machine".

## Artefacts

| Artefact | Shape | Pure fn of | Serialised | Tracked |
|---|---|---|---|---|
| `full_registry` | keyed map `concept_key -> Manifest`, relationships intact | `configs/` tree | JSON, sorted keys | yes — lock-style (PR diff shows manifest changes) |
| `filtered_registry` | same shape, restricted to subscriptions + concept `needs`-closure | `full_registry` + profile | JSON, sorted keys | no (depends on profile) |

Both are **injectable**: default = recompute; a prebuilt artefact may be
passed in instead (test / accountability / speed).

## Manifest parse — `MAN-*`

- **MAN-1** A concept directory MUST contain `_manifest.toml`; absence =
  `ManifestMissingError(path)` (ov#1 — silence is not legal).
- **MAN-2** Required: `name` (non-empty str); ≥1 `[[install]]`. Optional:
  `[check]`, 0..N `[[link]]`, `group`, `needs`.
- **MAN-3** `[[install]].kind`: omitted = package (requires `pkg`);
  `"config-only"` (forbids `pkg`); `"script"` (forbids `pkg`, implies an
  `install.sh` sibling). Wrong combination = `ManifestSchemaError`.
- **MAN-4** `when` keys ⊆ `{platform, manager}` only; any other key =
  `ManifestSchemaError` (ov#10 — no condition DSL).
- **MAN-5** `[[link]]`: `source` (a filename or `"."`), `dir`, `name`,
  `mode ∈ {link, copy}`. Missing required field = `ManifestSchemaError`.
- **MAN-6** `group` optional str = choice-group membership (ov#15).
- **MAN-7** `needs` = `list[str]`; entries kept **raw** (concept-key vs
  bare-package distinction is resolved later, not here).
- **MAN-8** Parsing is **pure and total**: returns a `Manifest` or a typed
  error carrying `(path, reason)`. It never raises an untyped exception and
  never reads anything outside the given file.

## Discover / `full_registry` — `FUL-*`

- **FUL-1** Discovery scans `configs/<group>/<concept>/_manifest.toml`. The
  `group` set is **explicit** (`tools, editors, shell, extras, managers,
  rules`), never inferred from the tree.
- **FUL-2** `concept_key` is unique across all groups; a collision =
  `RegistryError(duplicate key, paths)`.
- **FUL-3** `full_registry` is a **pure deterministic** function of the tree:
  the same tree yields byte-identical serialisation.
- **FUL-4** Relationships are **first-class and preserved** — `needs` edges
  and `group` membership are recorded, not flattened away (this is the
  "synergy between related concepts" requirement).
- **FUL-5** An unknown `needs` target is **not** an error here (it may be a
  bare package); the registry only *records*. Cross-concept edge validation
  is deferred to resolve.
- **FUL-6** One malformed manifest fails the **whole** build with the
  offending path — no partial registry (ov#4 hard-stop spirit).
- **FUL-7** Serialisation round-trips: `load(dump(r)) == r`; keys sorted;
  injectable (a prebuilt `full_registry` skips the scan).

## Filter / `filtered_registry` — `FIL-*`

- **FIL-1** Input: `full_registry` + parsed profile (subscription lists
  `tools/editors/extras/shell/managers`).
- **FIL-2** Every subscribed key MUST exist in `full_registry`; unknowns =
  `SubscriptionError` listing **all** unknowns (closed-world, ov#3).
- **FIL-3** Result = subscribed keys **plus their `needs`-closure that are
  themselves concepts** (recurse); bare-package `needs` are recorded, not
  pulled in as concepts (ov#11).
- **FIL-4** Choice-group rule: at most one subscribed concept per `group`;
  >1 = `ChoiceGroupError(group, members)`. Unsubscribed siblings of a
  subscribed group member are recorded for *derived teardown* (the teardown
  itself is computed later, ov#6/#15).
- **FIL-5** Same structure/relationships as `full_registry` — a subset, not a
  flattening.
- **FIL-6** Pure and deterministic given `(full_registry, profile)`;
  serialisable; injectable.
- **FIL-7** Filtering consults **no host state** (no detection). It raises
  only the errors that need no host: `SubscriptionError`, `ChoiceGroupError`.
  Platform/manager availability hard-stops belong to resolve.

## Errors

All typed, actionable, and **aggregated** — the build reports *every* failure
it can find before exiting, never stops at the first (better DX; matches the
plan-first accountability of ov#4):

`ManifestMissingError` · `ManifestSchemaError` · `RegistryError` (dup key) ·
`SubscriptionError` · `ChoiceGroupError`.

## Test obligations

- Fixture `configs/` trees: one valid, plus one per malformed variant
  (missing manifest, bad `kind`, illegal `when` key, missing link field,
  duplicate key).
- ≥1 test per `MAN-* / FUL-* / FIL-*` id.
- Golden serialisation of `full_registry` and `filtered_registry` over the
  fixture tree × the four `config-profiles/*.toml`.
- Properties: `load(dump(x)) == x`; identical tree → identical bytes;
  filtering is idempotent.
- No test in this spec may touch the real `$HOME` or probe the host — if a
  behaviour needs that, it belongs in `resolve.md`, not here.

## Handoff to `resolve.md` (not yet written)

`resolve(filtered_registry, SystemDescriptor, policy) -> Plan | ResolutionError`:
detection, avenue/manager selection (ov#5), platform availability hard-stop
(ov#3/#8), manager bootstrap (ov#14), `needs` topo-order (ov#11), choice-group
teardown materialisation, render/link/post-hook step emission.
