## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

## local
from utils import logging, shell_actions

##
## === EXTRA CONFIG
##

SCRIPT_NAME = Path(__file__).name
EXTRAS_DIR = Path(__file__).resolve().parent / "extras"

_log_message = logging.make_logger(SCRIPT_NAME)


@dataclass
class ExtraConfig:
    name: str
    source_path: Path
    target_path: Path
    platforms: tuple[str, ...]


EXTRAS: dict[str, ExtraConfig] = {
    "macos-keybindings": ExtraConfig(
        name="macOS keybindings",
        source_path=EXTRAS_DIR / "macos" / "DefaultKeyBinding.dict",
        target_path=Path.home() / "Library" / "KeyBindings" / "DefaultKeyBinding.dict",
        platforms=("darwin",),
    ),
}

##
## === EXTRA HELPERS
##


def extra_applies_to_platform(
    *,
    extra: ExtraConfig,
) -> bool:
    """Return whether the extra applies to the current platform."""
    return any(sys.platform.startswith(platform) for platform in extra.platforms)


def setup_extra(
    *,
    extra: ExtraConfig,
    dry_run: bool,
) -> None:
    """Symlink one extra config file if it applies to the current platform."""
    if not extra_applies_to_platform(extra=extra):
        _log_message(f"Skipping {extra.name}; not applicable on `{sys.platform}`.")
        return
    shell_actions.ensure_dir_exists(
        directory=extra.target_path.parent,
        script_name=SCRIPT_NAME,
        dry_run=dry_run,
    )
    shell_actions.create_symlink(
        source_path=extra.source_path,
        target_path=extra.target_path,
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
    _log_message("Started removing extra config symlinks")
    for extra in EXTRAS.values():
        shell_actions.remove_symlink(
            target_path=extra.target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    _log_message("Finished removing extra config symlinks")


def run(
    *,
    dry_run: bool,
) -> None:
    _log_message("Started setting up extra configs")
    for extra in EXTRAS.values():
        setup_extra(
            extra=extra,
            dry_run=dry_run,
        )
    _log_message("Finished setting up extra configs")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Symlink optional extra config files.",
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
