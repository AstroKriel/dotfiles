import argparse
import subprocess
from pathlib import Path
from utils.logging import log_message
from utils.shell_ops import create_symlink, ensure_dir_exists

SCRIPT_NAME = Path(__file__).name
TOOLS_DIR = Path(__file__).resolve().parent / "tools"
HOME_CONFIG_DIR = Path.home() / ".config"

TOOL_CONFIGS = {
  TOOLS_DIR / "ghostty" : HOME_CONFIG_DIR / "ghostty",
  TOOLS_DIR / "kitty"   : HOME_CONFIG_DIR / "kitty",
  TOOLS_DIR / "nvim"    : HOME_CONFIG_DIR / "nvim",
  TOOLS_DIR / "tmux"    : HOME_CONFIG_DIR / "tmux",
}

def _log_message(message: str):
  log_message(
    script_name = SCRIPT_NAME,
    message     = message
  )

def install_tpm_if_needed(*, dry_run: bool):
  tpm_path = HOME_CONFIG_DIR / "tmux" / "plugins" / "tpm"
  if tpm_path.exists():
    _log_message(f"TPM is already installed under: {tpm_path}")
    return
  if dry_run:
    _log_message(f"[dry-run] Would install TPM under: {tpm_path}")
    return
  _log_message(f"Installing TPM under: {tpm_path}")
  try:
    subprocess.run(
      args  = ["git", "clone", "https://github.com/tmux-plugins/tpm", str(tpm_path)],
      check = True
    )
  except subprocess.CalledProcessError:
    _log_message(f"Failed to clone TPM to: {tpm_path}")

def main():
  ## parse user inputs
  parser = argparse.ArgumentParser(description="Symlink config folders for Neovim, tmux, ghostty.")
  parser.add_argument("--dry-run", action="store_true", help="Print actions without applying them")
  args = parser.parse_args()
  dry_run = args.dry_run
  ## log start of script
  _log_message("Started setting up tool configs")
  ## symlink each config directory to ~/.config/
  for source_path, target_path in sorted(TOOL_CONFIGS.items()):
    ensure_dir_exists(
      directory   = target_path.parent,
      script_name = SCRIPT_NAME,
      dry_run     = dry_run
    )
    create_symlink(
      source_path = source_path,
      target_path = target_path,
      script_name = SCRIPT_NAME,
      dry_run     = dry_run
    )
  ## install TPM if needed
  install_tpm_if_needed(dry_run = dry_run)
  ## log end of script
  _log_message("Finished setting up tool configs")

if __name__ == "__main__":
  main()

## .