# Dynamic Registry and Install Planning

Decision record for the dynamic-registry and install-planning refactor.
Status: agreed, not built. Branch: `add/dynamic-registry`.

---

## Problem

Subscriptions in `this-system.toml` select concepts by key. The setup scripts
symlink config and silently skip a concept when its tool is absent from
`$PATH`. Installation lives entirely outside the repo and is undocumented.
The registries in `scripts/setup/{tools,editors}.py` hardcode every concept in
Python dicts, so a new concept requires a central edit, and per-OS knowledge
(`mac_app`, the renamed `DefaultKeyBinding.dict` target) already leaks into
those dicts.

The goal is to make concepts, including extras such as `conky` and `zathura`,
installable and self-describing, scaling to several operating systems without
a hand-maintained central registry.

---

## Decisions

| # | Decision | Why |
|---|---|---|
| 1 | Every concept has a `_manifest.toml` beside its config. A missing manifest is a validation error. | Silence is not a legal state; "assumed present" must be explicit. |
| 2 | The registry is derived by scanning `configs/<group>/<concept>/`, not from hardcoded dicts. | A new concept is a new directory; no central edit, no merge conflict, no drift. |
| 3 | Allow-list, closed-world. A manifest lists the systems it supports via ordered `[[install]]` avenues; no avenue resolving means unavailable. | A platform with no avenue is unsupported by construction; nothing to forget to deny. |
| 4 | Plan, then apply. Resolution is pure: `resolve(subscriptions, manifests, system) -> Plan or Error`. Any unresolvable subscription hard-stops the whole run. | A subscription that cannot be satisfied is a profile error, not a soft skip; no partial apply. |
| 5 | Resolver precedence (see "Resolver precedence"). | The manifest binds the avenue set; profile policy may reorder within it. |
| 6 | Actions are `install`, `render`, `link` or `copy`, `post-hook`. `check` is a gate, not an action. Teardown is derived, never declared. | These four cover every behaviour already in `scripts/setup/`. |
| 7 | One manifest per concept, with a `[[link]]` list of 1..N entries. `install`, `check`, `needs` are stated once. | The unit needing link metadata is a link; duplicating install across files would drift. |
| 8 | `config-only` is not the same as available-everywhere (see "Availability"). | "Needs an install action" and "where available" are independent axes. |
| 9 | Extras become concept directories (`configs/extras/<concept>/`), subscribed by key, not file path. | Extras, tools, and editors become the same kind of thing; this is the biggest refactor. |
| 10 | `when` is limited to `{platform, manager}`. The long tail uses one `kind = "script"` avenue. | An arbitrary predicate set becomes an imperative DSL by accident. |
| 11 | `needs` distinguishes a bare package from a concept (see "Dependencies"). | A bare package is installed; a concept is installed and linked. |
| 12 | Avenues key on manager, not OS. | The manager is always the discriminator; per-distro differences are different `pkg` per avenue. |
| 13 | Manager availability is detected, never declared (see "Manager rules"). | The profile is intent; the system descriptor is fact. A declared manager duplicates the platform tag and can lie. |
| 14 | Managers are installable concepts, bootstrapped only if subscribed (see "Manager rules"). | Bootstrapping a package manager is a heavy action; it must be explicit intent, never a side effect. |
| 15 | Choice groups: mutual exclusivity is declared, not inferred (see "Choice groups"). | Conflicts are explicit by declaration, never inferred from two concepts coinciding on a target. |
| 16 | The global default manager ranking lives in one shared place, the capability-map module. | One ranking, not duplicated per profile. |
| 17 | `needs` classification: a token names a concept if it is a key in `full_registry`, otherwise it is a bare package (see "Dependencies"). | One rule, no marker syntax; the registry is the single source of truth for what a concept is. |
| 18 | Generated artefacts (`full_registry`, `filtered_registry`, `plan`) serialise as JSON. Hand-written manifests and profiles stay TOML. | Generated files want canonical, stable, diffable output; humans do not edit them. |
| 19 | `full_registry` is committed as `registry.lock.json` at the repo root. `filtered_registry` and `plan` are gitignored, written under `build/` only with `--plan`, otherwise in-memory (see "Artefact format and tracking"). | The registry is deterministic from `configs/`, so a PR diff shows manifest changes; the other two depend on the host. |
| 20 | The group set is fixed: `tools, editors, shell, extras, managers, rules`. `configs/managers/` is a real group; `rules` is folded into discovery, retiring the separate `link_rules` path. | One discovery mechanism for every kind of concept. |
| 21 | Shell is modelled as `shell-common` (no group, always available) plus `shell-bash` and `shell-zsh` (both `group = "shell"`) (see "Groups and the shell model"). | The "remove the other shell" behaviour becomes ordinary choice-group teardown, not bespoke logic. |

---

## Resolver precedence

The manifest owns the acceptable avenue **set** (hard, closed-world). Within
that set the chosen avenue is decided in this order:

1. capability: managers detected present, intersected with platform candidates
2. manifest: the acceptable avenue set is binding
3. profile `prefer_managers`: orders within the set
4. manifest avenue order: default tie-break
5. global default ranking (macOS prefers `brew`)

The manifest order is a default, not binding; profile policy may reorder it.

Capability map: `platform -> [managers]` lists candidate managers per
platform; detection confirms which are actually present.

> The one-avenue and `kind = "script"` cases stay non-negotiable because the
> set has size one, so preference is moot.

Worked example. A manifest, a system, a profile, then the chosen avenue:

```toml
# manifest avenues, in declared order
[[install]]
when = { manager = "brew" }
pkg  = "fd"
[[install]]
when = { manager = "pacman" }
pkg  = "fd"
[[install]]
when = { manager = "cargo" }
pkg  = "fd-find"
```

```text
detected present : [pacman, cargo]   (brew absent)
profile          : prefer_managers = ["cargo"]
```

Resolution: capability removes the `brew` avenue (absent). The remaining set
is `[pacman, cargo]`. `prefer_managers` orders `cargo` first. Chosen avenue:
`cargo`, `pkg = "fd-find"`. Without the `prefer_managers` key the manifest
order would stand and `pacman` would win.

---

## Availability

`config-only` and available-everywhere are independent axes:

| Axis | Answered by |
|---|---|
| Needs an install action? | `kind` (`config-only` means no) |
| Where is it available? | the avenue's `when` |

Available-everywhere is `config-only` with no `when`. A macOS-only config file
is `config-only` with `when = { platform = "macos" }`.

Contrastive pair:

```toml
# everywhere: config-only, no `when`
[[install]]
kind = "config-only"
```

```toml
# macOS only: config-only, with `when`
[[install]]
when = { platform = "macos" }
kind = "config-only"
```

The first resolves on every platform. The second resolves on macOS only;
subscribed on Linux it produces `ResolutionError: only available on [macos]`.

---

## Dependencies

Classification rule (#17): a `needs` token names a concept if it is a key in
`full_registry`, otherwise it is a bare package. There is no marker syntax.

| `needs` entry | Classified as | Meaning |
|---|---|---|
| `lua` (no such concept key) | bare package | install only |
| `zathura` (a concept key) | concept | recurse: install and link that concept |

Worked pair. The same `needs` token classified two ways by the same rule:

```text
full_registry keys : { ..., "zathura", ... }   # no "lua" key

needs = ["lua"]      -> "lua" not a key      -> bare package -> install lua
needs = ["zathura"]  -> "zathura" is a key   -> concept      -> install + link zathura
```

Resolution order is topological; cycles are a hard error.

---

## Manager rules

The profile is intent (`platforms` plus subscriptions); the system descriptor
is fact (which candidate managers are present, found by detection). The
profile must never assert a manager. It may only:

| Key | Effect |
|---|---|
| `exclude_managers = [...]` | hard filter; removes detected managers |
| `prefer_managers = [...]` | non-exhaustive ordering hint; unlisted managers fall to the global default; inert if its target is absent |

The two keys stay separate: an ordered list tempts "unlisted means excluded",
and silent exclusion by omission is the implicit behaviour this design
rejects. With no keys, behaviour is pure detection.

`prefer_managers` is inert when its target is absent:

```text
profile : prefer_managers = ["aur"]

case A, aur present : detected [pacman, aur] -> reordered to [aur, pacman]
case B, aur absent  : detected [pacman]      -> unchanged [pacman]
```

In case B the preference installs nothing; it only orders what detection
already found.

Managers are themselves concepts with a manifest (`[check]` plus a bootstrap
`[[install]]`, usually `kind = "script"`). The profile gains a
`managers = [...]` subscription list. The planner bootstraps a missing manager
only if the profile subscribes to it. A tool whose only avenue needs an
absent, unsubscribed manager hard-stops; a manager is never installed
silently. Subscription means "provision if missing"; detection still decides
whether the bootstrap runs (idempotent via `[check]`). Base managers
(`pacman`, `dnf`, `apt`) are assumed present; subscribing to them is a no-op.
A bootstrap that needs a base manager (yay via pacman) is ordinary dependency
order.

---

## Choice groups

A manifest may declare `group = "<name>"` (for example `shell`,
`hpc-scheduler`). The resolver enforces at most one subscribed concept per
group, otherwise `ResolutionError`. The unsubscribed siblings' teardown is
derived. One mechanism covers both `bash` versus `zsh` (remove the other
shell) and `pbs` versus `slurm` (same target).

Worked pair, both manifests carrying `group = "shell"`:

```text
subscribe [shell-bash, shell-zsh]
  -> ChoiceGroupError(group="shell", members=["shell-bash","shell-zsh"])

subscribe [shell-zsh]
  -> shell-zsh resolves; shell-bash recorded as a derived teardown target
```

---

## Groups and the shell model

The group set is fixed (#20): `tools, editors, shell, extras, managers,
rules`. Discovery scans `configs/<group>/<concept>/` for exactly these.
`configs/managers/` is a real group; `rules` is discovered like any other,
retiring the separate `link_rules` path.

Shell is modelled as three concepts (#21):

| Concept | `group` | Availability |
|---|---|---|
| `shell-common` | none | always (the shared, shell-agnostic config) |
| `shell-bash` | `shell` | when `bash` is the chosen shell |
| `shell-zsh` | `shell` | when `zsh` is the chosen shell |

`shell-common` is always in the filtered registry. `shell-bash` and
`shell-zsh` are choice-group siblings, so subscribing one records the other
for derived teardown; the old bespoke "back up the other shell's files"
behaviour is now ordinary choice-group teardown.

---

## Pipeline architecture

One engine in `src/local_helpers/pipeline/`. The per-kind setup scripts are
thin filters over it (`run(kinds=["tools"])`), not duplicated logic.

Four stages, two serialisable artefacts crossing the seams:

| Stage | Module | Purity | In to out |
|---|---|---|---|
| 1 discover | `registry.py` | pure given a tree | `configs/` to **Registry** (all manifests, system-agnostic) |
| 2 detect | `detect.py` | impure | host to `SystemDescriptor` |
| 3 resolve | `resolve.py` | pure | (Registry, Profile, Descriptor) to **Plan** or `ResolutionError` |
| 4 execute | `execute.py` | impure | Plan to side effects (wraps `apply_shell_actions`) |

The two durable artefacts are the Registry and the Plan. The registry
filtered through the system-toml lens is the Plan; there is no third artefact.

Injection at every seam: by default each stage recomputes; any artefact may be
passed in instead. This yields three properties:

| Property | How injection provides it |
|---|---|
| test | feed a fake Registry, Descriptor, or Plan; stage 3 stays pure, so the profile-by-platform golden matrix needs no real machine |
| accountability | serialise the Plan, review it, then `execute` consumes that exact frozen Plan; apply cannot drift from what was reviewed |
| speed | skip rescans when nothing changed |

`setup_routine.py` is the thin two-phase driver: load profile, build registry
and descriptor, resolve. On `ResolutionError` it prints every error, exits
non-zero, and applies nothing; otherwise it executes. `--plan` runs stages 1
to 3 only.

Worked set, three concepts: `conky` needs the bare package `lua`; `shell-bash`
and `shell-zsh` carry `group = "shell"`. Profile subscribes `conky` and
`shell-zsh`. The three artefacts side by side show why the registry family
keeps relationships and the plan is flat:

```json
// full_registry.json  (every concept, relationships intact)
{
  "conky":      { "group": null,    "needs": ["lua"] },
  "shell-bash": { "group": "shell", "needs": [] },
  "shell-zsh":  { "group": "shell", "needs": [] }
}
```

```json
// filtered_registry.json  (subscribed, relationships still intact)
{
  "conky":     { "group": null,    "needs": ["lua"] },
  "shell-zsh": { "group": "shell", "needs": [] },
  "_teardown": ["shell-bash"]
}
```

```json
// plan.json  (flat ordered steps; relationships resolved away)
{
  "steps": [
    { "action": "install", "pkg": "lua" },
    { "action": "install", "concept": "conky" },
    { "action": "link",    "concept": "conky" },
    { "action": "install", "concept": "shell-zsh" },
    { "action": "link",    "concept": "shell-zsh" },
    { "action": "teardown","concept": "shell-bash" }
  ]
}
```

`filtered_registry` keeps `conky -> needs -> lua` and the `shell` group; the
plan has linearised them into ordered steps with `lua` before `conky` and the
choice-group teardown emitted.

---

## Artefact format and tracking

Generated artefacts serialise as JSON (#18); hand-written manifests and
profiles stay TOML. Tracking follows the intent-versus-fact split (#19):

| Artefact | Path | Tracked | Rationale |
|---|---|---|---|
| `full_registry` | `registry.lock.json` (repo root) | yes | deterministic from `configs/`; a PR diff shows manifest changes, like `uv.lock` |
| `filtered_registry` | `build/filtered_registry.json` | no | depends on the profile |
| `plan` | `build/plan.json` | no | depends on the host |

`filtered_registry` and `plan` are written under `build/` only when `--plan`
is passed; otherwise they stay in-memory. `build/` is gitignored.

---

## Schema

```
[check]                 # gate: is it present?
  command | macos_app | file

[[install]]             # ordered = preference; first satisfiable wins
  when = { platform=, manager= }
  kind = "config-only" | "script"   # omit = normal package install
  pkg  = "..."
  needs = ["..."]

[[link]]                # 1..N; each independently resolved
  when   = { platform= }
  source = "file" | "."   # "." = the whole directory
  dir    = "target dir"
  name   = "output name"  # may differ from source
  mode   = "link" | "copy"
```

---

## Manifest examples by case

### Install required, link many files, one platform-default install

```toml
# configs/tools/tmux/_manifest.toml
name = "Tmux"
[check]
command = "tmux"

[[install]]
when = { manager = "brew" }
pkg  = "tmux"
[[install]]
when = { manager = "pacman" }
pkg  = "tmux"

[[link]]
source = "tmux.conf"
dir    = "~/.config/tmux"
name   = "tmux.conf"
[[link]]
source = "conf"
dir    = "~/.config/tmux"
name   = "conf"
```

### No install, link one file, name rewritten (config-only, everywhere)

```toml
# configs/shell/shell-aliases/_manifest.toml
name = "Shell aliases"
[[install]]
kind = "config-only"          # no `when` = available everywhere

[[link]]
source = "shell_aliases"
dir    = "~"
name   = ".shell_aliases"     # renamed
```

### Whole-directory link (one `[[link]]`, `source = "."`)

```toml
# configs/tools/ghostty/_manifest.toml
name = "Ghostty"
[check]
command   = "ghostty"
macos_app = "Ghostty.app"

[[install]]
when = { manager = "brew" }
pkg  = "ghostty"

[[link]]
source = "."
dir    = "~/.config"
name   = "ghostty"
```

### Thin spec, one platform only, no install

```toml
# configs/extras/disable-navigation-keys/_manifest.toml
name = "Disable macOS navigation keys"
[[install]]
when = { platform = "macos" }
kind = "config-only"          # nothing to install

[[link]]
when   = { platform = "macos" }   # and only resolves on macOS
source = "disable-navigation-keys.dict"
dir    = "~/Library/KeyBindings"
name   = "DefaultKeyBinding.dict"
```

Subscribed on Linux, no avenue resolves: `ResolutionError: only available on
[macos]`, hard-stop.

### Specific method preferred, generic fallback

```toml
# configs/tools/foo/_manifest.toml
name = "Foo"
[check]
command = "foo"

[[install]]                   # specific: tried first because listed first
when = { manager = "script" }
kind = "script"               # configs/tools/foo/install.sh
[[install]]                   # generic fallback
when = { manager = "brew" }
pkg  = "foo"
[[install]]
when = { manager = "pacman" }
pkg  = "foo"
```

### Narrow install source, only obtainable one way

```toml
# configs/tools/bar/_manifest.toml
name = "Bar"
[check]
command = "bar"

[[install]]
when = { manager = "aur" }    # the only avenue
pkg  = "bar"
```

A box without AUR: no avenue resolves, hard-stop.

### Different manager per distro (manager-not-OS keying)

```toml
# configs/tools/fd/_manifest.toml
name = "fd"
[check]
command = "fd"

[[install]]
when = { manager = "pacman" }   # Arch
pkg  = "fd"
[[install]]
when = { manager = "dnf" }      # Fedora; only the pkg name differs
pkg  = "fd-find"
[[install]]
when = { manager = "brew" }
pkg  = "fd"

[[link]]
source = "."
dir    = "~/.config"
name   = "fd"
```

There is no "fedora" install branch; `pacman` versus `dnf` is the
discriminator. If the method differed (Fedora needing a COPR), the `dnf`
avenue would become `kind = "script"`. The capability map carries
`arch-x11 -> [pacman, aur]` and `fedora -> [dnf]`; detection confirms which is
present.

### A manager is itself a concept (bootstrap, only if subscribed)

```toml
# configs/managers/brew/_manifest.toml   subscribed via managers = ["brew"]
name = "Homebrew"
[check]
command = "brew"                # idempotent: skip bootstrap if present

[[install]]
when = { platform = "macos" }
kind = "script"                 # the brew install one-liner
```

```toml
# configs/managers/yay/_manifest.toml
name = "yay (AUR helper)"
[check]
command = "yay"

[[install]]
when  = { manager = "pacman" }  # bootstrap needs a base manager; ordinary dep
kind  = "script"
needs = ["base-devel", "git"]
```

Fresh Mac, profile `managers = ["brew"]`, `tmux` subscribed with a brew-only
avenue: the plan is `[bootstrap brew, brew install tmux, link ...]`. Dropping
the `brew` subscription gives `ResolutionError: tmux needs brew; absent and
not subscribed`.

### Dependency on another concept plus a bare package

```toml
# configs/tools/conky/_manifest.toml
name = "Conky"
[check]
command = "conky"

[[install]]
when  = { manager = "pacman" }
pkg   = "conky"
needs = ["lua"]               # bare package
[[link]]
source = "conky.conf"
dir    = "~/.config/conky"
name   = "conky.conf"
```

---

## Implementation order

1. Schema plus backfill of one or two concepts. No behaviour change.
2. Pure resolver plus the `system` type plus the profile-by-platform golden tests.
3. `--plan`: detect system, resolve, print the plan or hard-stop. Dry-run only.
4. Replace the hardcoded registries with directory discovery.
5. Restructure extras into concept directories.
6. Optional `--bootstrap`: execute a validated plan; idempotent via `[check]`.

---

## Still open

| Item | Lean |
|---|---|
| `--bootstrap` execution policy: run installs and manager bootstrap, or only print commands? | print-only default, execute opt-in per platform (bootstrap-ability itself is settled by #14) |
| A manifest that must force its avenue order regardless of profile `prefer_managers` (broken formula, mandatory script). Needs a per-avenue binding flag. | deferred until a real case appears (#5 covers it via a set of one today) |
| `render` declaration mechanism: explicit `[render]` table versus convention-discovered. Output location is settled by #6 (in-repo, committed). | decide at the second render case |

> Profile format migration (extras path to key, new manager keys) is an
> implementation note, not a design item: the parser must detect old-style
> entries and error clearly. It is a one-time hand-edit for a single-user repo.
