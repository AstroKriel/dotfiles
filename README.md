# dotfiles

Notes for setting up my dev environment on a fresh macOS or Linux machine.

This repo manages config for the following:

- **Shell:**
  - bash: works on almost all systems, including servers; a safe default
  - zsh: more plugin-friendly, better suited for personal devices
- **Editors:**
  - [Visual Studio Code](https://code.visualstudio.com): rich, full-featured editor with broad extension support
  - [Zed](https://zed.dev): minimal, fast editor built in Rust
- **Terminals:**
  - [Ghostty](https://ghostty.org): fast, native terminal emulator
  - [Kitty](https://sw.kovidgoyal.net/kitty/): GPU-accelerated terminal with tiling support
- **Tools:**
  - [tmux](https://github.com/tmux/tmux): terminal multiplexer; run multiple terminal sessions in one window
  - [Yazi](https://yazi-rs.github.io): terminal file manager
  - [Neovim](https://neovim.io): terminal-based text editor
  - [Doom](https://github.com/doomemacs/doomemacs) flavoured [Emacs](https://www.gnu.org/software/emacs/): text editor with sensible batteries-included

# Setup

Steps 1-3 are needed before cloning this repo: installing Homebrew (the package manager used throughout), uv (to run the setup scripts), and setting up GitHub SSH access. Steps 4-7 clone the repo and run the setup scripts to configure the shell, editors, and tools.

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

Generate an SSH key. Use a descriptive comment to identify it later. When prompted for a passphrase, just press Enter to skip it:

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

Re-run this at any time to confirm access, or view the public key again with:

```bash
cat ~/.ssh/id_ed25519_github.pub
```

## Step 4: Clone this repo

The repo can be cloned anywhere; the setup scripts resolve paths relative to the repo. The home directory is a good default:

```bash
git clone git@github.com:AstroKriel/dotfiles.git ~/dotfiles
```

## Step 5: Set up your shell

Choose `bash` or `zsh`, e.g.:

```bash
uv run setup_shell.py zsh
```

Open a new terminal to pick up the changes.

## Step 6: Set up editors

Install whichever editors are needed. Note: `--cask` is used for GUI applications (like editors and terminals); command-line tools are installed without it:

```bash
brew install --cask visual-studio-code
brew install --cask zed
```

Then run the setup script to merge and symlink config files and install extensions (skips editors not installed):

```bash
uv run setup_editors.py
```

## Step 7: Set up tools

Install whichever tools are needed:

```bash
brew install neovim
brew install tmux
brew install --cask emacs
brew install --cask ghostty
brew install --cask kitty
brew install yazi ffmpeg
```

Then run the setup script to symlink config files. Any tools not installed will be skipped automatically:

```bash
uv run setup_tools.py
```

To check which tools are detected without applying any changes:

```bash
uv run setup_tools.py --check-only
```

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

# Dry run mode

All setup scripts support `--dry-run` to preview actions without applying them:

```bash
uv run setup_shell.py bash --dry-run
uv run setup_editors.py --dry-run
uv run setup_tools.py --dry-run
```

Pass `-h` to any script to see all available arguments:

```bash
uv run setup_shell.py -h
uv run setup_editors.py -h
uv run setup_tools.py -h
```
