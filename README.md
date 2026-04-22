# DotFiles

This repo is used to set up my dev environment on a fresh macOS or Linux machine, and is managed through the scripts discussed below. The main entry point is run as:

```bash
uv run setup_configs.py [args]
```

Layer modules can be run directly with `uv run -m setup.<layer> [args]`.

All scripts support `--dry-run` to preview what actions will be performed, without actually applying them. For a first-time machine setup, see the [full setup guide](#full-setup-guide) below.

The active system profile is selected by `this-system.toml`, which is intentionally ignored by git. Usually this should be a symlink to a tracked profile under `profiles/`:

```bash
ln -s profiles/arch-x11.toml this-system.toml
```

Copying a tracked profile to `this-system.toml` also works. The setup scripts do not accept a one-off profile flag; update `this-system.toml` when changing the system's long-term profile.

Profiles subscribe to repo-visible config names. Editors and tools use their folder names, while extras use paths relative to `extras/`:

```toml
editors = ["zed"]
tools = ["ghostty"]
extras = ["arch-x11/touchpad-workspace-gestures.conf"]
```

`setup_configs.py` is the main entry point. It orchestrates the profile-backed layer modules under `setup/`: shell, tools, editors, and extras.

`uv run -m setup.shell` sets the login shell from `this-system.toml` and applies its config files, supporting [bash](https://www.gnu.org/software/bash/manual/bash.html) and [zsh](https://zsh.sourceforge.io/Doc/). Use it to pick up shell config changes.

`uv run -m setup.tools` wires up configs for subscribed tools, clones required plugin repos, and runs post-setup steps like `tmux`. It configures tools but does not install them, so subscribed tools that are not installed yet are skipped. Pass `--which <name>` to apply one subscribed tool, or `--all` to apply every subscribed tool in `this-system.toml`; omitting both is an error. Add `--check-only` to report which selected tools are detected without applying changes. The following tools are supported:
- [Ghostty](https://ghostty.org): fast, native terminal emulator
- [Kitty](https://sw.kovidgoyal.net/kitty/): GPU-accelerated terminal with tiling support
- [tmux](https://github.com/tmux/tmux): terminal multiplexer; run multiple terminal sessions in one window — requires [`tmux-mem-cpu-load`](https://github.com/thewtex/tmux-mem-cpu-load) to be installed separately for CPU/memory stats in the status bar (`paru -S tmux-mem-cpu-load` on Arch)
- [Yazi](https://yazi-rs.github.io): terminal file manager

`uv run -m setup.editors` installs extensions and applies configs for subscribed editors, including [Visual Studio Code](https://code.visualstudio.com), [Zed](https://zed.dev), [Neovim](https://neovim.io), and [Doom](https://github.com/doomemacs/doomemacs) flavoured [Emacs](https://www.gnu.org/software/emacs/). Subscribed editors not yet on the system are skipped. Pass `--which <name>` to apply one subscribed editor, or `--all` to apply every subscribed editor in `this-system.toml`; omitting both is an error.

For Zed and VS Code, edit the module files under `settings/`, `keymap/`, or `keybindings/`, then run `uv run -m setup.editors --which zed` or `uv run -m setup.editors --which vscode` to regenerate the tracked JSON files. Do not hand-edit generated `settings.json`, `keymap.json`, or `keybindings.json` as canonical config.

`uv run -m setup.extras` applies optional platform-specific configs, such as macOS keybindings. Pass `--which <extras-relative-path>` to apply one subscribed extra, or `--all` to apply every subscribed extra in `this-system.toml`; omitting both is an error.

`uv run -m setup.rules` links tracked rule files into `~/.rules/`.

`setup_configs.py` runs the full setup chain (shell, tools, editors, and extras) in one command. Pass `--check-profile` to validate `this-system.toml` without changing the system, or `--remove-symlinks` to tear everything down.

# Full Setup Guide

Steps 1-3 are needed before cloning this repo: installing Homebrew (the package manager used throughout), uv (to run the setup scripts), and setting up GitHub SSH access. Steps 4-6 clone the repo, install tools, and run the setup scripts to configure the shell, editors, tools, and extras.

## Step 1: Install Homebrew

**macOS:** first install Xcode command line tools (provides `git`, `make`, etc.):

```bash
xcode-select --install
```

**Linux:** install the required system dependencies (`git` for version control, `build-essential` for compilers and build tools that Homebrew relies on):

```bash
sudo apt update && sudo apt install -y git build-essential
```

**Both platforms:** install [Homebrew](https://brew.sh):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Linux:** Homebrew installs to `/home/linuxbrew/.linuxbrew`, which is not on the default `$PATH`. The installer prints instructions at the end for how to add it; follow those before continuing.

## Step 2: Install uv

[uv](https://github.com/astral-sh/uv) is used to manage the Python dependencies for this repo; install it via:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal so `uv` is in your `$PATH`.

## Step 3: Set up GitHub SSH access

Generate an SSH key. Use a descriptive comment to identify it later. When prompted for a passphrase, you can set one for extra security, but note it down, since you will need to type it every time you use the key. If that sounds like friction you don't want, just press Enter to use an empty passphrase:

```bash
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519_github -C "for github ssh access from <device-name> created on <YYYY-MM-DD>"
```

This creates two files. Keep the private key secret and never share it; the public key is what you paste into services like GitHub to prove your identity:
- `~/.ssh/id_ed25519_github` (private key)
- `~/.ssh/id_ed25519_github.pub` (public key)

Create `~/.ssh/config` if needed, and append the following to tell SSH which key to use for GitHub:

```
Host github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```

Copy the public key to the clipboard:

```bash
# macOS
pbcopy < ~/.ssh/id_ed25519_github.pub

# Linux
cat ~/.ssh/id_ed25519_github.pub
```

Add it to the GitHub account: **Settings > SSH and GPG keys > New SSH key**.

Verify the connection:

```bash
ssh -T git@github.com
```

You should see: `Hi <username>! You've successfully authenticated...`

## Step 4: Clone this repo

The repo can be cloned anywhere; the setup scripts resolve paths relative to the repo. The home directory is a good default:

```bash
git clone git@github.com:AstroKriel/DotFiles.git
```

## Step 5: Install tools and editors

Install whichever tools and editors are needed. Note: `--cask` is used for GUI applications; command-line tools are installed without it:

```bash
# editors
brew install --cask visual-studio-code
brew install --cask zed
brew install neovim
brew install --cask emacs

# terminals
brew install --cask ghostty
brew install --cask kitty

# tools
brew install tmux
brew install yazi ffmpeg
```

## Step 6: Run setup

```bash
cd DotFiles
ln -s profiles/arch-x11.toml this-system.toml
uv run setup_configs.py
```

Open a new terminal to pick up the shell changes.

# Verify your setup

After completing all steps, confirm the key dependencies are in place:

```bash
brew --version         # Homebrew
git --version          # Git
uv --version           # uv
ssh -T git@github.com  # GitHub SSH access (expect: "Hi <username>!")
```

Confirm the shell config was applied correctly (`type` is a shell built-in that shows how a command is resolved):

```bash
# when using bash
type reload_bash

# when using zsh
type reload_zsh
```

# Python Development

Python project metadata and tooling live in `pyproject.toml`. Run the main checks with:

```bash
uv run basedpyright
uv run python -m py_compile setup_configs.py setup/*.py utils/*.py
```
