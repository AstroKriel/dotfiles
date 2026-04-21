## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from dataclasses import dataclass
from pathlib import Path
## local
from utils import profiles
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
    requires: tuple[str, ...] = ()


EXTRAS: dict[str, ExtraConfig] = {
    "macos-disable-navigation-keys": ExtraConfig(
        name="macOS disabled navigation keys",
        source_path=EXTRAS_DIR / "macos" / "disable-navigation-keys.dict",
        target_path=Path.home() / "Library" / "KeyBindings" / "DefaultKeyBinding.dict",
        requires=("macos",),
    ),
    "x11-mouse-buttons": ExtraConfig(
        name="X11 mouse buttons",
        source_path=EXTRAS_DIR / "arch-x11" / "xbindkeysrc",
        target_path=Path.home() / ".xbindkeysrc",
        requires=("linux", "x11"),
    ),
    "x11-touchpad-gestures": ExtraConfig(
        name="X11 touchpad gestures",
        source_path=EXTRAS_DIR / "arch-x11" / "libinput-gestures.conf",
        target_path=Path.home() / ".config" / "libinput-gestures.conf",
        requires=("linux", "x11", "xfce"),
    ),
    "x11-locale-profile": ExtraConfig(
        name="X11 locale profile",
        source_path=EXTRAS_DIR / "arch-x11" / "xprofile",
        target_path=Path.home() / ".xprofile",
        requires=("linux", "x11", "lightdm"),
    ),
}

##
## === EXTRA HELPERS
##


def extra_requirements_are_met(
    *,
    extra: ExtraConfig,
    platform_tags: tuple[str, ...] | None,
) -> bool:
    """Return whether the active system profile satisfies the extra requirements."""
    if platform_tags is None:
        return True
    return set(extra.requires).issubset(platform_tags)


def setup_extra(
    *,
    extra: ExtraConfig,
    dry_run: bool,
    platform_tags: tuple[str, ...] | None = None,
) -> None:
    """Symlink one extra config file if the active profile satisfies its requirements."""
    if not extra_requirements_are_met(
        extra=extra,
        platform_tags=platform_tags,
    ):
        missing = sorted(set(extra.requires) - set(platform_tags or ()))
        _log_message(f"Skipping {extra.name}; missing profile platform tag(s): {', '.join(missing)}")
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


def get_selected_extras(
    *,
    selected: tuple[str, ...] | None,
) -> dict[str, ExtraConfig]:
    """Return extra configs selected by the active system profile."""
    if selected is None:
        return EXTRAS
    unknown = sorted(set(selected) - set(EXTRAS))
    if unknown:
        raise KeyError(f"Unknown extra(s): {', '.join(unknown)}")
    return {
        extra_key: EXTRAS[extra_key]
        for extra_key in selected
    }

##
## === PROGRAM MAIN
##


def remove_symlinks(
    *,
    dry_run: bool,
    selected: tuple[str, ...] | None = None,
) -> None:
    _log_message("Started removing extra config symlinks")
    selected_extras = get_selected_extras(selected=selected)
    for extra in selected_extras.values():
        shell_actions.remove_symlink(
            target_path=extra.target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    _log_message("Finished removing extra config symlinks")


def run(
    *,
    dry_run: bool,
    selected: tuple[str, ...] | None = None,
    platform_tags: tuple[str, ...] | None = None,
) -> None:
    _log_message("Started setting up extra configs")
    selected_extras = get_selected_extras(selected=selected)
    for extra in selected_extras.values():
        setup_extra(
            extra=extra,
            dry_run=dry_run,
            platform_tags=platform_tags,
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
    parser.add_argument(
        "--profile",
        help="Load selected extras from profiles/<name>.toml",
    )
    args = parser.parse_args()
    profile = profiles.load_profile(profile_name=args.profile)
    run(
        dry_run=args.dry_run,
        selected=profile.extras if profile is not None else None,
        platform_tags=profile.platforms if profile is not None else None,
    )

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
