## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from pathlib import Path

## local
import setup_editors
import setup_extras
import setup_shell
import setup_tools
from utils import profiles

##
## === SCRIPT CONFIG
##

SCRIPT_NAME = Path(__file__).name

##
## === PROGRAM MAIN
##


def main():
    parser = argparse.ArgumentParser(
        description="Set up the full dotfiles environment from a system profile.",
    )
    parser.add_argument(
        "shell",
        nargs="?",
        choices=[s.name for s in setup_shell.SHELLS],
        help="Shell to activate, overriding the selected profile shell",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without applying them",
    )
    parser.add_argument(
        "--remove-symlinks",
        action="store_true",
        help="Remove dotfile symlinks for the selected profile, or all if no profile exists",
    )
    parser.add_argument(
        "--profile",
        help="Load selected configs from profiles/<name>.toml",
    )
    args = parser.parse_args()
    dry_run = args.dry_run
    profile = profiles.load_profile(
        profile_name=args.profile,
        required=not args.remove_symlinks,
    )
    shell = args.shell or (profile.shell if profile is not None else None)
    if shell is None and not args.remove_symlinks:
        parser.error("shell is required unless set by profile or --remove-symlinks is specified")
    if args.remove_symlinks:
        setup_shell.remove_symlinks(
            dry_run=dry_run,
        )
        setup_tools.remove_symlinks(
            dry_run=dry_run,
            selected=profile.tools if profile is not None else None,
        )
        setup_editors.remove_symlinks(
            dry_run=dry_run,
            selected=profile.editors if profile is not None else None,
        )
        setup_extras.remove_symlinks(
            dry_run=dry_run,
            selected=profile.extras if profile is not None else None,
        )
    else:
        setup_shell.run(
            shell=shell,
            dry_run=dry_run,
        )
        setup_tools.run(
            dry_run=dry_run,
            selected=profile.tools,
        )
        setup_editors.run(
            dry_run=dry_run,
            selected=profile.editors,
        )
        setup_extras.run(
            dry_run=dry_run,
            selected=profile.extras,
            platform_tags=profile.platforms,
        )

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
