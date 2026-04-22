## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from pathlib import Path

## local
from utils import log_messages, apply_shell_actions

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


def run(
    *,
    dry_run: bool,
) -> None:
    _log_message(f"Linking all rules from {RULES_DIR} to {TARGET_DIR}")
    link_all_rules(dry_run=dry_run)
    _log_message("Done.")


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
    run(dry_run=args.dry_run)

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
