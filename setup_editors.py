import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from utils.logging import log_message
from utils.shell_ops import create_symlink, ensure_dir_exists

SCRIPT_NAME  = Path(__file__).name
DOTFILES_DIR = Path(__file__).resolve().parent / "editors"

EDITORS = {
  "vscode": {
    "name": "Visual Studio Code",
    "command": "code",
    "brew": "visual-studio-code --cask",
    "dotfiles_dir": DOTFILES_DIR / "vscode",
    "target_dir": Path.home() / "Library/Application Support/Code/User", # macOS
    "files": {
      "settings": "dict",
      "keybindings": "list"
    }
  },
  "zed": {
    "name": "Zed",
    "command": "zed",
    "brew": "zed --cask",
    "dotfiles_dir": DOTFILES_DIR / "zed",
    "target_dir": Path.home() / ".config/zed/",
    "files": {
      "settings": "dict",
      "keymap": "list"
    }
  }
}

## see for details
## https://kevinyank.com/posts/fix-system-beep-vscode/
## https://blog.victormendonca.com/2020/04/27/how-to-change-macos-key-bindings/
## https://gist.github.com/trusktr/1e5e516df4e8032cbc3d
MAC_KEYBIND_FILE_NAME = "DefaultKeyBinding.dict"
MAC_KEYBIND_TARGET_DIR  = Path.home() / "Library" / "KeyBindings"
MAC_KEYBIND_SOURCE_PATH = DOTFILES_DIR / MAC_KEYBIND_FILE_NAME
MAC_KEYBIND_TARGET_PATH = MAC_KEYBIND_TARGET_DIR / MAC_KEYBIND_FILE_NAME

def _log_message(message: str):
  log_message(script_name=SCRIPT_NAME, message=message)

def filter_jsonc_comments(content: str) -> str:
  content = re.sub(r'/\*[\s\S]*?\*/', '', content) # remove block comments
  content = re.sub(r'//[^\n\r]*', '', content) # remove line comments
  return content

def merge_config_modules(
    *,
    modules_dir : Path,
    mode        : str
  ) -> dict | list:
  if mode == "dict":
    merged = {}
  elif mode == "list":
    merged = []
  else:
    _log_message(f"Error: Unsupported mode `{mode}`")
    return None
  if not modules_dir.exists():
    _log_message(f"Skipping. No module directory found: {modules_dir}")
    return None
  for module in sorted(modules_dir.glob("*.jsonc")):
    with module.open("r", encoding="utf-8") as f:
      raw_content = f.read()
      filtered_content = filter_jsonc_comments(raw_content)
      content = json.loads(filtered_content)
      if mode == "dict":
        merged.update(content)
      elif mode == "list":
        merged.extend(content)
  return merged

def setup_editor(name, meta, dry_run):
  _log_message(f"Started setting up {name}")
  ## check whether the editor is installed
  if shutil.which(meta["command"]):
    _log_message(f"Found {meta['name']} ({meta['command']}) in your `$PATH`.")
  else:
    _log_message(
      f"{meta['command']} was not found in your `$PATH`.\n"
      f"Install it via: `brew install {meta['brew']}`"
    )
    return
  for file_name, mode in meta["files"].items():
    modules_dir = meta["dotfiles_dir"] / file_name
    merged_config = merge_config_modules(
      modules_dir = modules_dir,
      mode        = mode
    )
    if merged_config is None:
      return
    output_path = meta["dotfiles_dir"] / f"{file_name}.json"
    target_path = meta["target_dir"] / f"{file_name}.json"
    if dry_run:
      _log_message(f"[dry-run] Would write merged settings to: {output_path}")
    else:
      with output_path.open("w", encoding="utf-8") as f:
        json.dump(merged_config, f, indent=2)
      _log_message(f"Wrote merged config to: {output_path}")
    ## ensure target directory exists
    ensure_dir_exists(
      directory   = meta["target_dir"],
      script_name = SCRIPT_NAME,
      dry_run     = dry_run
    )
    ## symlink merged config
    create_symlink(
      source_path = output_path,
      target_path = target_path,
      script_name = SCRIPT_NAME,
      dry_run     = dry_run
    )

def main():
  parser = argparse.ArgumentParser(description="Generate and symlink vs-code settings.")
  parser.add_argument("--dry-run", action="store_true", help="Print actions without applying them")
  args = parser.parse_args()
  dry_run = args.dry_run
  for name, meta in EDITORS.items():
    setup_editor(name, meta, dry_run)
  if sys.platform.startswith("darwin"):
    _log_message("Applying macOS keybindings (override to fix Electron shortcut conflict).")
    ensure_dir_exists(
      directory   = MAC_KEYBIND_TARGET_DIR,
      script_name = SCRIPT_NAME,
      dry_run     = args.dry_run,
    )
    create_symlink(
      source_path = MAC_KEYBIND_SOURCE_PATH,
      target_path = MAC_KEYBIND_TARGET_PATH,
      script_name = SCRIPT_NAME,
      dry_run     = args.dry_run,
    )
  _log_message("Finished setting up editors.")

if __name__ == "__main__":
  main()

## .