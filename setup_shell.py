import os
import shutil
import argparse
import subprocess
from pathlib import Path
from utils.shell_ops import create_symlink, backup_file
from utils.logging import log_message

SCRIPT_NAME = Path(__file__).name
SHELL_DIR   = Path(__file__).resolve().parent / "shell"
HOME_DIR    = Path.home()
SHELL_FILES = {
  "bash": {
    "files": ["bashrc", "bash_options", "bash_prompt", "inputrc"],
    "dir": "bash"
  },
  "zsh": {
    "files": ["zshrc", "zsh_options", "zsh_prompt"],
    "dir": "zsh"
  },
  "shared": {
    "files": ["shell_aliases", "shell_functions", "shell_options", "shell_paths"],
    "dir": "utils"
  }
}

def remove_file_if_exists(
    target_path : Path,
    dry_run     : bool
  ):
  if target_path.exists() or target_path.is_symlink():
    backup_file(
      target_path = target_path,
      script_name = SCRIPT_NAME,
      dry_run     = dry_run
    )

def change_login_shell(
    shell   : str,
    dry_run : bool = False
  ):
  shell_path = shutil.which(shell)
  if not shell_path:
    log_message(
      script_name = SCRIPT_NAME,
      message     = f"Shell '{shell}' not found in PATH."
    )
    return
  current_shell = os.environ.get("SHELL", "")
  if current_shell != shell_path:
    message = f"Changing login shell to: {shell_path}"
    if dry_run:
      log_message(
        script_name = SCRIPT_NAME,
        message     = f"[dry-run] Would {message}"
      )
    else:
      subprocess.run(["chsh", "-s", shell_path], check=True)
      log_message(
        script_name = SCRIPT_NAME,
        message     = message
      )
  else:
    log_message(
      script_name = SCRIPT_NAME,
      message     = f"Login shell is already set to: {shell_path}"
    )


def main():
  ## parse user inputs
  parser = argparse.ArgumentParser(description="Symlink shell configuration files.")
  parser.add_argument("shell", choices=["bash", "zsh"], help="Shell to activate")
  parser.add_argument("--dry-run", action="store_true", help="Print actions without applying them")
  args = parser.parse_args()
  ## define parameters
  shell = args.shell
  dry_run = args.dry_run
  other_shell = "zsh" if (shell == "bash") else "bash"
  ## log start of script
  log_message(
    script_name = SCRIPT_NAME,
    message     = "Started running!"
  )
  ## link shared config files
  for fname in SHELL_FILES["shared"]["files"]:
    source_path = SHELL_DIR / SHELL_FILES["shared"]["dir"] / fname
    target_path = HOME_DIR / f".{fname}"
    create_symlink(
      source_path = source_path,
      target_path = target_path,
      script_name = SCRIPT_NAME,
      dry_run     = dry_run
    )
  ## link config files for the selected shell env
  for fname in SHELL_FILES[shell]["files"]:
    source_path = SHELL_DIR / SHELL_FILES[shell]["dir"] / fname
    target_path = HOME_DIR / f".{fname}"
    create_symlink(
      source_path = source_path,
      target_path = target_path,
      script_name = SCRIPT_NAME,
      dry_run     = dry_run
    )
  ## remove config files for the other shell env
  for fname in SHELL_FILES[other_shell]["files"]:
    target_path = HOME_DIR / f".{fname}"
    remove_file_if_exists(
      target_path = target_path,
      dry_run     = dry_run
    )
  ## update default login shell env
  change_login_shell(
    shell   = shell,
    dry_run = dry_run
  )
  ## log end of script
  log_message(
    script_name = SCRIPT_NAME,
    message     = "Finished!"
  )

if __name__ == "__main__":
  main()

## .