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

---

## Availability

`config-only` and available-everywhere are independent axes:

| Axis | Answered by |
|---|---|
| Needs an install action? | `kind` (`config-only` means no) |
| Where is it available? | the avenue's `when` |

Available-everywhere is `config-only` with no `when`. A macOS-only config file
is `config-only` with `when = { platform = "macos" }`.

---

## Dependencies

| `needs` entry | Meaning |
|---|---|
| bare package (e.g. `lua`) | install only |
| concept (e.g. `zathura`) | recurse: install and link that concept |

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
