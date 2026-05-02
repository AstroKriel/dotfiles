# DotFiles

DotFiles configures a development environment from a local system profile. The repo tracks reusable shell, editor, tool, rules, and platform extras. The active machine chooses which pieces apply through `this-system.toml`.

Main entry points:

```bash
uv run setup_configs.py
uv run -m setup.<layer> <args>
```

All setup commands support `--dry-run` where the layer exposes it.

---

## Bootstrap

Install the base tools needed to clone the repo and run setup commands.

| Platform | Command |
|---|---|
| macOS | `xcode-select --install` |
| Arch Linux | `sudo pacman -S git base-devel` |
| Debian or Ubuntu | `sudo apt update && sudo apt install -y git build-essential` |

Package managers are intentionally not hard-coded into the setup scripts. Use the native package manager for the system unless a specific tool requires another source.

Install `uv`, then open a new terminal so `uv` is available on `PATH`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

---

## Git Access

Generate an SSH key for Git hosting:

```bash
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519_github -C "GitHub access from <device-name> created on <YYYY-MM-DD>"
```

Create or edit `~/.ssh/config`:

```sshconfig
Host github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```

Add the public key to the Git hosting account, then verify access:

```bash
cat ~/.ssh/id_ed25519_github.pub
ssh -T git@github.com
```

> **Note:** GitHub prints an authentication success message and then exits without opening a shell. That is expected.

---

## Clone the Repo

Clone the repo wherever source repositories normally live:

```bash
git clone git@github.com:AstroKriel/DotFiles.git
cd DotFiles
```

---

## Select a Profile

`this-system.toml` selects the active system profile and is ignored by git. Usually it is a symlink to a tracked profile under `profiles/`.

```bash
ln -s profiles/<profile-name>.toml this-system.toml
```

Copying a tracked profile to `this-system.toml` also works:

```bash
cp profiles/<profile-name>.toml this-system.toml
```

Validate the selected profile before applying changes:

```bash
uv run setup_configs.py --check-profile
```

Profiles subscribe to config groups:

```toml
shell = "zsh"
platforms = ["linux", "x11"]
editors = ["zed"]
tools = ["ghostty"]
extras = ["arch-x11/touchpad-workspace-gestures.conf"]
```

| Profile key | Purpose |
|---|---|
| `shell` | Login shell managed by `setup.shell` |
| `platforms` | Capability tags used to gate platform-specific extras |
| `editors` | Editor configs to apply |
| `tools` | Tool configs to apply |
| `extras` | Optional files or scripts under `extras/` |
| `link_rules` | Whether tracked rules are linked into `~/.rules/` |
| `set_login_shell` | Whether setup should call `chsh` for the selected shell |

---

## Install Applications

The setup scripts configure applications, but they do not install every application package. Install the shell, editors, tools, and extras required by the selected profile before running the full setup.

Example package commands:

```bash
# macOS with Homebrew
brew install tmux ffmpeg
brew install --cask ghostty zed

# Arch Linux
sudo pacman -S tmux yazi ffmpeg zed
```

> **Note:** Some packages have different names or sources across systems. Install equivalent applications for the selected profile rather than treating the examples as mandatory.

---

## Run Setup

Apply the full selected profile:

```bash
uv run setup_configs.py
```

Open a new terminal after shell changes are applied.

Remove managed symlinks for the selected profile:

```bash
uv run setup_configs.py --remove-symlinks
```

---

## Layer Commands

Use the main script to apply every subscribed layer in the active profile:

```bash
uv run setup_configs.py
```

Use layer modules directly when changing only one part of the setup. Direct layer runs use Python module execution, so include `-m`.

| Layer | Command | Purpose |
|---|---|---|
| Shell | `uv run -m setup.shell` | Applies the selected shell config |
| Tools | `uv run -m setup.tools --which <tool>` | Applies one subscribed `<tool>` |
| Editors | `uv run -m setup.editors --which <editor>` | Applies one subscribed `<editor>` |
| Extras | `uv run -m setup.extras --which <extras-relative-path>` | Applies one subscribed extra |
| Rules | `uv run -m setup.rules` | Links rules into `~/.rules/` |

Run all subscribed entries for a single layer:

```bash
uv run -m setup.tools --all
uv run -m setup.editors --all
uv run -m setup.extras --all
```

Check which subscribed tools are installed before applying tool configs:

```bash
uv run -m setup.tools --check-only --all
```

---

## Editing Generated Config

Some editor configs are generated from smaller tracked modules.

| Editor | Config | Canonical files | Generated file |
|---|---|---|---|
| Zed | Settings | `editors/zed/settings/*.jsonc` | `editors/zed/settings.json` |
| Zed | Keymap | `editors/zed/keymap/*.jsonc` | `editors/zed/keymap.json` |
| VS Code | Settings | `editors/vscode/settings/*.jsonc` | `editors/vscode/settings.json` |
| VS Code | Keybindings | `editors/vscode/keybindings/*.jsonc` | `editors/vscode/keybindings.json` |

Regenerate after editing module files:

```bash
uv run -m setup.editors --which zed
uv run -m setup.editors --which vscode
```

> **Note:** Treat generated JSON files as output. Edit the module files instead.

---

## Verify Setup

Confirm the base commands are available:

```bash
git --version
uv --version
ssh -T git@github.com
```

Confirm shell helpers are linked:

```bash
type reload_bash
type reload_zsh
```

> **Note:** Only one of `reload_bash` or `reload_zsh` will exist, depending on the selected shell.

---

## Design Decisions

| Decision | Reason |
|---|---|
| Use `this-system.toml` instead of command-line profile flags | The active profile is a long-term machine choice, not a one-off run option |
| Keep package installation outside setup scripts | Package names and installers differ across systems |
| Use profile subscriptions | The repo can contain more configs than any one system needs |
| Use platform tags for extras | Platform-specific files are skipped when the active profile does not satisfy their requirements |
| Generate large editor JSON files from modules | Smaller files are easier to review and edit |
