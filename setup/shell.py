## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import shutil

## local
from utils import log_messages, apply_shell_actions

##
## === SHELL CONFIG
##

SCRIPT_NAME = Path(__file__).name
ROOT_DIR = Path(__file__).resolve().parent.parent
SHELL_DIR = ROOT_DIR / "shell"
HOME_DIR = Path.home()

_log_message = log_messages.make_logger(SCRIPT_NAME)


@dataclass
class ShellConfig:
    name: str
    files: list[str]


UTILS_FILES = ["shell_aliases", "shell_functions", "shell_options", "shell_paths"]

SHELLS = [
    ShellConfig(
        name="bash",
        files=["bash_profile", "bashrc", "bash_options", "bash_prompt", "inputrc"],
    ),
    ShellConfig(
        name="zsh",
        files=["zshrc", "zsh_options", "zsh_prompt"],
    ),
]

##
## === SHELL HELPERS
##


def remove_file_if_exists(
    *,
    target_path: Path,
    dry_run: bool,
):
    if target_path.exists() or target_path.is_symlink():
        apply_shell_actions.backup_file(
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
        apply_shell_actions.run_command(
            args=["chsh", "-s", shell_path],
            script_name=SCRIPT_NAME,
            description=f"change login shell to: {shell_path}",
            dry_run=dry_run,
            capture_output=False,
        )
    else:
        ## shell is already correctly set
        _log_message(f"Login shell is already set to: {shell_path}")

##
## === PROGRAM MAIN
##


def remove_symlinks(
    *,
    dry_run: bool,
):
    log_messages.configure(write_to_file=not dry_run)
    _log_message("Started removing shell config symlinks")
    all_files = UTILS_FILES + [f for s in SHELLS for f in s.files]
    for file_name in all_files:
        apply_shell_actions.remove_symlink(
            target_path=HOME_DIR / f".{file_name}",
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    _log_message("Finished removing shell config symlinks")


def run(
    *,
    shell: str,
    dry_run: bool,
):
    log_messages.configure(write_to_file=not dry_run)
    chosen = next(s for s in SHELLS if s.name == shell)
    others = [s for s in SHELLS if s.name != shell]
    ## log start of script
    _log_message("Started running!")
    ## link shared config files
    for file_name in UTILS_FILES:
        source_path = SHELL_DIR / "utils" / file_name
        target_path = HOME_DIR / f".{file_name}"
        apply_shell_actions.create_symlink(
            source_path=source_path,
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    ## link config files for the selected shell env
    for file_name in chosen.files:
        source_path = SHELL_DIR / chosen.name / file_name
        target_path = HOME_DIR / f".{file_name}"
        apply_shell_actions.create_symlink(
            source_path=source_path,
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    ## remove config files for other shell envs
    for s in others:
        for file_name in s.files:
            remove_file_if_exists(
                target_path=HOME_DIR / f".{file_name}",
                dry_run=dry_run,
            )
    ## update default login shell env
    change_login_shell(
        shell=chosen.name,
        dry_run=dry_run,
    )
    ## log end of script
    _log_message("Finished!")


def main():
    ## parse user inputs
    parser = argparse.ArgumentParser(
        description="Symlink shell configuration files.",
    )
    parser.add_argument(
        "shell",
        choices=[s.name for s in SHELLS],
        help="Shell to activate",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without applying them",
    )
    args = parser.parse_args()
    run(
        shell=args.shell,
        dry_run=args.dry_run,
    )

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
