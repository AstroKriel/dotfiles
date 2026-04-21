# DotFiles

This repo is used to set up my dev environment on a fresh macOS or Linux machine, and is managed through the scripts discussed below, where each is run via:

```bash
uv run <script>.py [args]
```

All scripts support `--dry-run` to preview what actions will be performed, without actually applying them. For a first-time machine setup, see the [full setup guide](#full-setup-guide) below.

The active system profile is selected by `this-system.toml`, which is intentionally ignored by git. Usually this should be a symlink to a tracked profile under `profiles/`:

```bash
ln -s profiles/arch-x11.toml this-system.toml
```

Pass `--profile <name>` to use `profiles/<name>.toml` directly for one command.

Profiles subscribe to repo-visible config names. Editors and tools use their folder names, while extras use paths relative to `extras/`:

```toml
editors = ["zed"]
tools = ["ghostty"]
extras = ["arch-x11/touchpad-workspace-gestures.conf"]
```

`setup_shell.py` sets the login shell and applies its config files, supporting [bash](https://www.gnu.org/software/bash/manual/bash.html) and [zsh](https://zsh.sourceforge.io/Doc/). Use it to switch shells or to pick up config changes.

`setup_tools.py` wires up configs for subscribed tools, clones required plugin repos, and runs post-setup steps like `tmux`. It configures tools but does not install them, so subscribed tools that are not installed yet are skipped; pass `--check-only` to report what subscribed tools are detected. Use `--tool <name>` for a one-off subscribed tool, or `--all` to ignore tool subscriptions. The following tools are supported:
- [Ghostty](https://ghostty.org): fast, native terminal emulator
- [Kitty](https://sw.kovidgoyal.net/kitty/): GPU-accelerated terminal with tiling support
- [tmux](https://github.com/tmux/tmux): terminal multiplexer; run multiple terminal sessions in one window — requires [`tmux-mem-cpu-load`](https://github.com/thewtex/tmux-mem-cpu-load) to be installed separately for CPU/memory stats in the status bar (`paru -S tmux-mem-cpu-load` on Arch)
- [Yazi](https://yazi-rs.github.io): terminal file manager

`setup_editors.py` installs extensions and applies configs for subscribed editors, including [Visual Studio Code](https://code.visualstudio.com), [Zed](https://zed.dev), [Neovim](https://neovim.io), and [Doom](https://github.com/doomemacs/doomemacs) flavoured [Emacs](https://www.gnu.org/software/emacs/). Subscribed editors not yet on the system are skipped. Use `--editor <name>` for a one-off subscribed editor, or `--all` to ignore editor subscriptions.

For Zed and VS Code, edit the module files under `settings/`, `keymap/`, or `keybindings/`, then run `uv run setup_editors.py` to regenerate the tracked JSON files. Do not hand-edit generated `settings.json`, `keymap.json`, or `keybindings.json` as canonical config.

`setup_extras.py` applies optional platform-specific configs, such as macOS keybindings. Use `--extra <extras-relative-path>` for a one-off subscribed extra, or `--all` to ignore extra subscriptions.

`setup_env.py` runs the full setup chain (shell, tools, editors, and extras) in one command. Pass `bash` or `zsh` for initial setup on a new machine, `--check-profile` to validate the selected profile without changing the system, or `--remove-symlinks` to tear everything down.

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
uv run setup_env.py zsh
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
