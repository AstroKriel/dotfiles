import os
import shutil
import argparse
import subprocess
from pathlib import Path
from utils.logging import log_message
from utils.shell_ops import create_symlink, backup_file

SCRIPT_NAME = Path(__file__).name
SHELL_DIR = Path(__file__).resolve().parent / "shell"
HOME_DIR = Path.home()
SHELL_FILES = {
    "bash": ["bashrc", "bash_options", "bash_prompt", "inputrc"],
    "zsh": ["zshrc", "zsh_options", "zsh_prompt"],
    "utils": ["git_options", "shell_aliases", "shell_functions", "shell_options", "shell_paths"],
}


def _log_message(message: str):
    log_message(
        script_name=SCRIPT_NAME,
        message=message,
    )


def remove_file_if_exists(
    *,
    target_path: Path,
    dry_run: bool,
):
    if target_path.exists() or target_path.is_symlink():
        backup_file(
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )


def change_login_shell(
    *,
    shell: str,
    dry_run: bool = False,
):
    ## resolve full path to shell binary
    shell_path = shutil.which(shell)
    if not shell_path:
        ## shell not found: log warning and exit
        _log_message(f"Shell '{shell}' not found in PATH.")
        return
    ## check if shell is already set
    current_shell = os.environ.get("SHELL", "")
    if current_shell != shell_path:
        message = f"Changing login shell to: {shell_path}"
        if dry_run:
            ## print what would happen
            _log_message(f"[dry-run] Would {message}")
        else:
            ## run chsh to update default shell
            subprocess.run(["chsh", "-s", shell_path], check=True)
            _log_message(message)
    else:
        ## shell is already correctly set
        _log_message(f"Login shell is already set to: {shell_path}")


def main():
    ## parse user inputs
    parser = argparse.ArgumentParser(description="Symlink shell configuration files.")
    parser.add_argument("shell", choices=["bash", "zsh"], help="Shell to activate")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without applying them")
    args = parser.parse_args()
    ## define parameters
    chosen_shell = args.shell
    dry_run = args.dry_run
    other_shell = "zsh" if (chosen_shell == "bash") else "bash"
    ## log start of script
    _log_message("Started running!")
    ## link shared config files
    for file_name in SHELL_FILES["utils"]:
        source_path = SHELL_DIR / "utils" / file_name
        target_path = HOME_DIR / f".{file_name}"
        create_symlink(
            source_path=source_path,
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    ## link config files for the selected shell env
    for file_name in SHELL_FILES[chosen_shell]:
        source_path = SHELL_DIR / chosen_shell / file_name
        target_path = HOME_DIR / f".{file_name}"
        create_symlink(
            source_path=source_path,
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    ## remove config files for the other shell env
    for file_name in SHELL_FILES[other_shell]:
        target_path = HOME_DIR / f".{file_name}"
        remove_file_if_exists(
            target_path=target_path,
            dry_run=dry_run,
        )
    ## update default login shell env
    change_login_shell(
        shell=chosen_shell,
        dry_run=dry_run,
    )
    ## log end of script
    _log_message("Finished!")


if __name__ == "__main__":
    main()

## .
