## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from pathlib import Path

## local
import setup_editors
import setup_shell
import setup_tools

##
## === SCRIPT CONFIG
##

SCRIPT_NAME = Path(__file__).name

##
## === PROGRAM MAIN
##


def main():
    parser = argparse.ArgumentParser(
        description="Set up the full dotfiles environment: shell, tools, and editors.",
    )
    parser.add_argument(
        "shell",
        nargs="?",
        choices=[s.name for s in setup_shell.SHELLS],
        help="Shell to activate (required unless --remove_symlinks is specified)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without applying them",
    )
    parser.add_argument(
        "--remove_symlinks",
        action="store_true",
        help="Remove all dotfile symlinks",
    )
    args = parser.parse_args()
    dry_run = args.dry_run
    if args.remove_symlinks:
        setup_shell.remove_symlinks(dry_run=dry_run)
        setup_tools.remove_symlinks(dry_run=dry_run)
        setup_editors.remove_symlinks(dry_run=dry_run)
    elif args.shell:
        setup_shell.run(shell=args.shell, dry_run=dry_run)
        setup_tools.run(dry_run=dry_run)
        setup_editors.run(dry_run=dry_run)
    else:
        parser.error("shell is required unless --remove_symlinks is specified")

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
