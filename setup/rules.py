## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from pathlib import Path
from typing import cast

## local
from utils import apply_shell_actions, log_messages

##
## === CONFIG
##

SCRIPT_NAME = Path(__file__).name
ROOT_DIR = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT_DIR / "rules"
TARGET_DIR = Path.home() / ".rules"

_log_message = log_messages.make_logger(SCRIPT_NAME)

##
## === CORE LOGIC
##


def link_all_rules(
    *,
    dry_run: bool,
) -> None:
    """Symlink all rule files from the dotfiles into ~/.rules/, preserving substructure."""
    for source_path in sorted(RULES_DIR.rglob("*.md")):
        relative_path = source_path.relative_to(RULES_DIR)
        target_path = TARGET_DIR / relative_path
        apply_shell_actions.ensure_dir_exists(
            directory=target_path.parent,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
        apply_shell_actions.create_symlink(
            source_path=source_path,
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )


##
## === PROGRAM MAIN
##


def remove_symlinks(
    *,
    dry_run: bool,
) -> None:
    log_messages.configure(write_to_file=not dry_run)
    _log_message(
        log_messages.format_dry_run(
            message="Started removing rule symlinks",
            dry_run=dry_run,
        ),
    )
    for target_path in sorted(TARGET_DIR.rglob("*.md")):
        apply_shell_actions.remove_symlink(
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    _log_message(
        log_messages.format_dry_run(
            message="Finished removing rule symlinks",
            dry_run=dry_run,
        ),
    )


def run(
    *,
    dry_run: bool,
) -> None:
    log_messages.configure(write_to_file=not dry_run)
    _log_message(
        log_messages.format_dry_run(
            message="Started linking rules",
            dry_run=dry_run,
        ),
    )
    link_all_rules(dry_run=dry_run)
    _log_message(
        log_messages.format_dry_run(
            message="Finished linking rules",
            dry_run=dry_run,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Symlink all rule files into ~/.rules/, preserving substructure.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without applying them",
    )
    args = parser.parse_args()
    dry_run = cast(bool, args.dry_run)
    run(dry_run=dry_run)


##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
