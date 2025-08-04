import json
import shutil
import argparse
from pathlib import Path
from utils.logging import log_message
from utils.shell_ops import create_symlink, ensure_dir_exists

SCRIPT_NAME          = Path(__file__).name
VSCODE_TARGET_DIR    = Path.home()  / "Library/Application Support/Code/User" # macOS
DOTFILES_DIR         = Path(__file__).resolve().parent / "vscode"
SETTINGS_CONFIG_DIR  = DOTFILES_DIR / "config"
MERGED_SETTINGS_PATH = DOTFILES_DIR / "settings.json"
KEYBINDINGS_PATH     = DOTFILES_DIR / "keybindings.json"

def _log_message(message: str):
  log_message(script_name=SCRIPT_NAME, message=message)

def merge_config_settings() -> dict:
  settings = {}
  for json_file in sorted(SETTINGS_CONFIG_DIR.glob("*.json")):
    with json_file.open("r", encoding="utf-8") as f:
      data = json.load(f)
      settings.update(data)
  return settings

def main():
  ## parse user inputs
  parser = argparse.ArgumentParser(description="Generate and symlink vs-code settings.")
  parser.add_argument("--dry-run", action="store_true", help="Print actions without applying them")
  args = parser.parse_args()
  dry_run = args.dry_run
  _log_message("Started running the vs-code setup")
  ## check vs-code has been installed
  if shutil.which("code"):
    _log_message("Found vs-code (code) in your `$PATH`.")
  else:
    _log_message(
      "vs-code was not found in your `$PATH`.\n"
      "Please install it from https://code.visualstudio.com/\n"
      "or via: `brew install --cask visual-studio-code`"
    )
    return
  ## merge modularised configs into a single collection
  _log_message(f"Merging settings from: {SETTINGS_CONFIG_DIR}")
  settings_dict = merge_config_settings()
  if dry_run:
    _log_message(f"[dry-run] Would write merged settings to: {MERGED_SETTINGS_PATH}")
  else:
    with MERGED_SETTINGS_PATH.open("w", encoding="utf-8") as f:
      json.dump(settings_dict, f, indent=2)
    _log_message(f"Wrote merged settings to: {MERGED_SETTINGS_PATH}")
  ## ensure vscode directory exists
  ensure_dir_exists(
    directory   = VSCODE_TARGET_DIR,
    script_name = SCRIPT_NAME,
    dry_run     = dry_run
  )
  ## symlink merged settings
  create_symlink(
    source_path = MERGED_SETTINGS_PATH,
    target_path = VSCODE_TARGET_DIR / "settings.json",
    script_name = SCRIPT_NAME,
    dry_run     = dry_run
  )
  ## symlink keybindings
  create_symlink(
    source_path = KEYBINDINGS_PATH,
    target_path = VSCODE_TARGET_DIR / "keybindings.json",
    script_name = SCRIPT_NAME,
    dry_run     = dry_run
  )
  _log_message("Finished vs-code setup")

if __name__ == "__main__":
  main()

## .