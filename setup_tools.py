import shutil
import argparse
import subprocess
from pathlib import Path
from utils.logging import log_message
from utils.shell_ops import create_symlink, ensure_dir_exists

HOME_DIR = Path.home()
SCRIPT_NAME = Path(__file__).name
DOTFILES_DIR = Path(__file__).resolve().parent / "tools"
CONFIG_DIR = HOME_DIR / ".config"

TOOLS = {
    "emacs": {
        "name": "Emacs (GUI)",
        "brew": "emacs --cask",
        "dotfiles_dir": DOTFILES_DIR / "emacs",
        "target_dir": HOME_DIR / ".doom.d",
        "clone_repo": {
            "name": "Doom-Emacs",
            "url": "https://github.com/doomemacs/doomemacs",
            "output": CONFIG_DIR / "emacs",
        },
        "post_setup": "doom_sync",
    },
    "tmux": {
        "name": "Tmux",
        "brew": "tmux",
        "dotfiles_dir": DOTFILES_DIR / "tmux",
        "target_dir": CONFIG_DIR / "tmux",
        "clone_repo": {
            "name": "TPM",
            "url": "https://github.com/tmux-plugins/tpm",
            "output": CONFIG_DIR / "tmux" / "plugins" / "tpm",
        },
    },
    "nvim": {
        "name": "Neovim",
        "brew": "neovim",
        "dotfiles_dir": DOTFILES_DIR / "nvim",
        "target_dir": CONFIG_DIR / "nvim",
    },
    "kitty": {
        "name": "Kitty terminal",
        "brew": "kitty --cask",
        "dotfiles_dir": DOTFILES_DIR / "kitty",
        "target_dir": CONFIG_DIR / "kitty",
    },
    "ghostty": {
        "name": "Ghostty terminal",
        "brew": "ghostty --cask",
        "dotfiles_dir": DOTFILES_DIR / "ghostty",
        "target_dir": CONFIG_DIR / "ghostty",
    },
    "yazi": {
        "name": "Yazi",
        "brew": "yazi ffmpeg",
        "dotfiles_dir": DOTFILES_DIR / "yazi",
        "target_dir": CONFIG_DIR / "yazi",
    },
}


def _log_message(message: str):
    log_message(
        script_name=SCRIPT_NAME,
        message=message,
    )


def check_installed_tools():
    _log_message("Checking installed tools...")
    available = set()
    for command, meta in TOOLS.items():
        if shutil.which(command):
            _log_message(f"Found {meta['name']} ({command}) in your `$PATH`.")
            available.add(command)
        else:
            _log_message(
                f"{meta['name']} was not found in your `$PATH`.\n"
                f"Install it via: `brew install {meta['brew']}`",
            )
    return available


def shallow_clone_repo(
    *,
    repo_name: str,
    repo_url: str,
    output_dir: Path,
    dry_run: bool,
):
    if output_dir.exists():
        _log_message(f"{repo_name} already exists under: {output_dir}")
        return
    if dry_run:
        _log_message(f"[dry-run] Would shallow clone {repo_name} under: {output_dir}")
        return
    _log_message(f"Cloning {repo_name} (shallow) under {output_dir}")
    try:
        subprocess.run(
            args=["git", "clone", "--depth", "1", repo_url,
                  str(output_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        _log_message(f"Successfully cloned {repo_name} under: {output_dir}")
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else "(no stderr output)"
        _log_message(f"Failed to clone {repo_name} ({repo_url}) under: {output_dir}\n{error_output}")


def run_doom_sync(dry_run: bool):
    doom_bin = CONFIG_DIR / "emacs" / "bin" / "doom"
    if not doom_bin.exists():
        _log_message(f"Doom binary not found at: {doom_bin}")
        return
    if dry_run:
        _log_message("[dry-run] Would run `doom sync`")
        return
    _log_message("Running `doom sync`")
    try:
        subprocess.run(
            args=[str(doom_bin), "sync"],
            check=True,
        )
        _log_message("Successfully ran `doom sync`")
    except subprocess.CalledProcessError as e:
        _log_message(f"Failed to run `doom sync` with exit code {e.returncode}")


def main():
    ## parse user inputs
    parser = argparse.ArgumentParser(
        description=
        "Symlink config folders and clone needed repos for: Neovim, tmux, Emacs, ghostty, and kitty."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without applying them")
    parser.add_argument("--check-only", action="store_true", help="Only check installed tools and exit")
    args = parser.parse_args()
    dry_run = args.dry_run
    ## log start of script
    _log_message("Started setting up tool configs")
    available_tools = check_installed_tools()
    if args.check_only:
        _log_message("Check complete. Exiting due to `--check-only`")
        return
    ## symlink each config directory to ~/.config/
    for tool in sorted(available_tools):
        meta = TOOLS[tool]
        ensure_dir_exists(
            directory=meta["target_dir"].parent,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
        create_symlink(
            source_path=meta["dotfiles_dir"],
            target_path=meta["target_dir"],
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    ## git clone repos
    for tool in available_tools:
        meta = TOOLS[tool]
        if "clone_repo" in meta:
            repo = meta["clone_repo"]
            shallow_clone_repo(
                repo_name=repo["name"],
                repo_url=repo["url"],
                output_dir=repo["output"],
                dry_run=dry_run,
            )
    if "emacs" in available_tools and TOOLS["emacs"].get("post_setup") == "doom_sync":
        run_doom_sync(dry_run)
    ## log end of script
    _log_message("Finished setting up tool configs")


if __name__ == "__main__":
    main()

## .
