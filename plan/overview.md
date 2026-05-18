# DotFiles — Dynamic Registry & Install Planning

Decision record for the dynamic-registry / install-planning refactor.
Status: agreed, not built. Branch: `add/dynamic-registry`.

## Decisions

1. **Every concept has a `_manifest.toml`** next to its config. No manifest =
   validation error (no implicit "assumed present").
2. **Registry is derived** by scanning `configs/<group>/<concept>/`, not from
   hardcoded Python dicts.
3. **Allow-list / closed-world.** A manifest lists the systems it *supports*
   via ordered `[[install]]` avenues. No avenue resolves → unavailable, by
   construction. "Only works one way" = one avenue. No deny markers.
4. **Plan, then apply.** Resolution is a pure function
   `resolve(subscriptions, manifests, system) -> Plan | Error`. If any
   subscribed concept can't resolve, hard-stop the whole run — no partial
   apply. Detection of the real system is a separate impure layer.
5. **Resolver precedence.** Manifest owns the acceptable avenue *set* (hard,
   closed-world); within that set the chosen avenue is decided by, in order:
   1. capability — managers detected present (∩ platform candidates, #5a)
   2. manifest — the acceptable avenue *set* is binding
   3. profile `prefer_managers = [...]` — orders within the set
   4. manifest avenue order — default tie-break
   5. global default ranking (mac prefers brew)

   The manifest's *order* is a default, not binding — profile policy may
   reorder it. The one-avenue / `kind=script` cases stay non-negotiable
   because the set has size 1 (preference is moot).
   5a. capability map: `platform -> [managers]` = *candidate* managers per
   platform; detection confirms which are actually present.
6. **Actions:** `install`, `render` (build output, e.g. Zed merges jsonc),
   `link|copy`, `post-hook` (e.g. set login shell). `check` is a gate, not an
   action. Teardown is derived, never declared. **Render output is written
   into the tracked `configs/` tree and committed** (status quo; no gitignored
   build dir). Consequence accepted: a post-setup `M configs/.../settings.json`
   is by design, not drift to fix.
7. **One manifest per concept**, with a `[[link]]` list (1..N). `install` /
   `check` / `needs` stated once.
8. **`config-only` ≠ available-everywhere.** Two independent axes:
   - needs an install action? → `kind` (`config-only` = no)
   - where available? → the avenue's `when`
9. **Extras must become concept dirs** (`configs/extras/<concept>/`,
   subscribed by key, not file path) to join the registry. Biggest refactor.
10. `when` is limited to `{ platform, manager }`. Long tail → one
    `kind = "script"` avenue. No condition DSL.
11. `needs = ["lua"]` (bare package) vs `needs = ["concept"]` (recurse:
    install + link). Topological order; cycles are a hard error.
12. **Avenues key on manager, not OS.** Arch→`pacman`, Fedora→`dnf`; the tool
    lists one avenue per manager. Per-distro package-name differences are just
    different `pkg` per avenue. An OS `platform` predicate is only for things
    that differ by OS but aren't the package source (link targets, OS-only
    config). No "fedora vs arch" install branching — the manager is always the
    discriminator.
13. **Manager availability is detected, never declared.** Profile = intent
    (`platforms` + subscriptions); the system descriptor = fact (which
    candidate managers are actually present, found by the impure detection
    layer). The profile must never *assert* a manager (it would duplicate the
    platform tag and can lie). It may only:
    - `exclude_managers = [...]` — hard filter; removes detected managers.
    - `prefer_managers = [...]` — non-exhaustive ordering hint; unlisted
      managers fall to the global default. Inert if its target is absent —
      preference orders what's present, it never installs anything.

    Keep the two keys separate (an ordered list tempts "unlisted = excluded",
    and silent exclusion-by-omission is the implicit behavior we reject).
    Default (no keys) = pure detection.
14. **Managers are installable concepts, bootstrapped only if subscribed.**
    A manager has its own manifest (`[check]` + a bootstrap `[[install]]`,
    usually `kind="script"`). The profile gains a `managers = [...]`
    subscription list. The planner bootstraps a missing manager **iff the
    profile subscribes to it**. A tool whose only avenue needs an absent,
    *unsubscribed* manager → hard-stop (never a silent manager install).
    Subscription = "provision if missing" (intent); detection still decides
    if the bootstrap actually runs (idempotent via `[check]`) — no conflict
    with #13's "never assert presence". Base managers (`pacman`/`dnf`/`apt`)
    are assumed-present; subscribing to them is a no-op. A bootstrap that
    needs a base manager (yay via pacman) is ordinary dependency order (#11).
15. **Choice groups (mutual exclusivity declared, not inferred).** A manifest
    may declare `group = "<name>"` (e.g. `shell`, `hpc-scheduler`). Resolver
    rule: **at most one subscribed concept per group**, else `ResolutionError`;
    the unsubscribed siblings' teardown is derived (#6). One mechanism covers
    both `bash`/`zsh` ("remove the other shell") and `pbs`/`slurm` (same
    target). Conflicts are explicit by declaration, never inferred from two
    concepts coinciding on a link target.
16. **Global default manager ranking lives in one shared place** — the
    capability-map module alongside `platform -> [managers]` (#5a), not
    duplicated per profile. Closes the prior open question.

## Pipeline architecture

One engine in `src/local_helpers/pipeline/`; the per-kind setup scripts are
thin filters over it (`run(kinds=["tools"])`), not duplicated logic.

Four stages, two **serializable** artefacts crossing the seams:

| Stage | Module | Purity | In → Out |
|---|---|---|---|
| 1 discover | `registry.py` | pure given a tree | `configs/` → **Registry** (all manifests, system-agnostic) |
| 2 detect | `detect.py` | impure | host → `SystemDescriptor` |
| 3 resolve | `resolve.py` | **pure** | (Registry, Profile, Descriptor) → **Plan** \| `ResolutionError` |
| 4 execute | `execute.py` | impure | Plan → side effects (wraps `apply_shell_actions`) |

- The two durable artefacts are **Registry** and **Plan**. The "registry
  filtered through the system-toml lens" *is* the Plan; no third artefact.
- **Injection at every seam.** Default = recompute (scan → detect → resolve).
  Any artefact may be passed in instead. This yields all three goals at once:
  - *test* — feed fake Registry/Descriptor/Plan; stage 3 stays 100% pure → the
    profile×platform golden matrix needs no real machine.
  - *accountability* — serialize the Plan, review it, then `execute` consumes
    **that exact frozen Plan**; apply cannot drift from what was reviewed.
  - *speed* — skip rescans when nothing changed.
- `setup_routine.py` is the thin two-phase driver: load profile → (registry,
  descriptor) → resolve → on `ResolutionError` print all + exit non-zero,
  apply nothing → else execute. `--plan` = stages 1–3 only.

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

## Manifest examples (by case)

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

### No install, link one file, name rewritten (`config-only`, everywhere)
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

### Thin/narrow spec — one platform only, no install
```toml
# configs/extras/disable-navigation-keys/_manifest.toml
name = "Disable macOS navigation keys"
[[install]]
when = { platform = "macos" }
kind = "config-only"          # nothing to install…

[[link]]
when   = { platform = "macos" }   # …and only resolves on macOS
source = "disable-navigation-keys.dict"
dir    = "~/Library/KeyBindings"
name   = "DefaultKeyBinding.dict"
```
Subscribed on Linux → `ResolutionError: only available on [macos]`, hard-stop.

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

### Narrow install source — only obtainable one way
```toml
# configs/tools/bar/_manifest.toml
name = "Bar"
[check]
command = "bar"

[[install]]
when = { manager = "aur" }    # the only avenue
pkg  = "bar"
```
Box without AUR → no avenue resolves → hard-stop.

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
when = { manager = "dnf" }      # Fedora — only the pkg name differs
pkg  = "fd-find"
[[install]]
when = { manager = "brew" }
pkg  = "fd"

[[link]]
source = "."
dir    = "~/.config"
name   = "fd"
```
No "fedora" install branch — `pacman` vs `dnf` is the discriminator. If the
*method* differed (e.g. Fedora needs a COPR), the dnf avenue becomes
`kind = "script"`. `platform -> [managers]` map carries `arch-x11 -> [pacman,
aur]`, `fedora -> [dnf]`; detection confirms which is actually present.

### A manager is itself a concept (bootstrap, only if subscribed)
```toml
# configs/managers/brew/_manifest.toml   — subscribed via `managers = ["brew"]`
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
when  = { manager = "pacman" }  # bootstrap needs a base manager — ordinary dep
kind  = "script"
needs = ["base-devel", "git"]
```
Fresh Mac, profile `managers=["brew"]` + tmux subbed (brew-only avenue):
plan = `[bootstrap brew, brew install tmux, link…]`. Drop the `brew`
subscription → `ResolutionError: tmux needs brew; absent and not subscribed`.

### Dependency on another concept + a bare package
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

## Implementation order

1. Schema + backfill 1–2 concepts. No behavior change.
2. Pure resolver + `system` type + profile×platform golden tests.
3. `--plan`: detect system → resolve → print plan or hard-stop. Dry-run only.
4. Replace hardcoded registries with directory discovery.
5. Restructure extras into concept dirs.
6. Optional `--bootstrap`: execute a validated plan; idempotent via `[check]`.

## Still open

- `--bootstrap` execution policy: actually run installs/manager bootstrap, or
  only print commands? Lean: print-only default, execute opt-in per platform.
  (Manager *bootstrap-ability* is settled by #14; only run-vs-print is open.)
- A manifest that must force its avenue order regardless of profile
  `prefer_managers` (e.g. "brew formula broken, script mandatory"). Needs a
  per-avenue binding flag. Deferred until a real case appears (#5 covers it
  via set-of-1 today).
- `render` *declaration* mechanism: explicit `[render]` table vs
  convention-discovered. (Output *location* settled by #6: in-repo, committed.)
  Decide at 2nd render case.
- Profile format migration (extras path→key, new manager keys) is an
  implementation note, not a design item: the parser must detect old-style
  entries and error clearly. One-time hand-edit (single-user repo).
