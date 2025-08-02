import json
import argparse
from pathlib import Path
from utils.logging import log_message
from utils.shell_ops import create_symlink, ensure_dir_exists

SCRIPT_NAME = Path(__file__).name
DOTFILES_DIR = Path(__file__).resolve().parent
INPUT_DIR = DOTFILES_DIR / "vscode" / "config"
OUTPUT_FILE = DOTFILES_DIR / "vscode" / "settings.json"
TARGET_FILE = Path.home() / "Library/Application Support/Code/User/settings.json" # macOS

def _log_message(message: str):
  log_message(script_name=SCRIPT_NAME, message=message)

def merge_config_settings() -> dict:
  settings = {}
  for json_file in sorted(INPUT_DIR.glob("*.json")):
    with json_file.open("r", encoding="utf-8") as f:
      data = json.load(f)
      settings.update(data)
  return settings

def main():
  ## parse user inputs
  parser = argparse.ArgumentParser(description="Generate and symlink VS Code settings.")
  parser.add_argument("--dry-run", action="store_true", help="Print actions without applying them")
  args = parser.parse_args()
  dry_run = args.dry_run
  _log_message("Started VS Code setup")
  ## merge modularised configs into a single collection
  _log_message(f"Merging settings from: {INPUT_DIR}")
  settings = merge_config_settings()
  ## write output
  if dry_run:
    _log_message(f"[dry-run] Would write merged settings to: {OUTPUT_FILE}")
  else:
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
      json.dump(settings, f, indent=2)
    _log_message(f"Wrote merged settings to: {OUTPUT_FILE}")
  ## ensure vscode directory exists
  ensure_dir_exists(
    directory   = TARGET_FILE.parent,
    script_name = SCRIPT_NAME,
    dry_run     = dry_run
  )
  ## symlink merged settings in place
  create_symlink(
    source_path = OUTPUT_FILE,
    target_path = TARGET_FILE,
    script_name = SCRIPT_NAME,
    dry_run     = dry_run
  )
  _log_message("Finished VS-Code setup")

if __name__ == "__main__":
  main()

## .