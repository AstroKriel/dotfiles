## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from dataclasses import dataclass
from pathlib import Path
## local
from utils import load_profiles
from utils import log_messages, apply_shell_actions

##
## === EXTRA CONFIG
##

SCRIPT_NAME = Path(__file__).name
ROOT_DIR = Path(__file__).resolve().parent.parent
EXTRAS_DIR = ROOT_DIR / "extras"

_log_message = log_messages.make_logger(SCRIPT_NAME)


@dataclass
class ExtraConfig:
    name: str
    source_path: Path
    target_path: Path
    requires: tuple[str, ...] = ()


EXTRAS: dict[str, ExtraConfig] = {
    "macos/disable-navigation-keys.dict": ExtraConfig(
        name="macOS disabled navigation keys",
        source_path=EXTRAS_DIR / "macos" / "disable-navigation-keys.dict",
        target_path=Path.home() / "Library" / "KeyBindings" / "DefaultKeyBinding.dict",
        requires=("macos",),
    ),
    "arch-x11/mouse-workspace-buttons.xbindkeysrc": ExtraConfig(
        name="xbindkeys mouse buttons",
        source_path=EXTRAS_DIR / "arch-x11" / "mouse-workspace-buttons.xbindkeysrc",
        target_path=Path.home() / ".xbindkeysrc",
        requires=("linux", "x11"),
    ),
    "arch-x11/touchpad-workspace-gestures.conf": ExtraConfig(
        name="libinput-gestures workspaces",
        source_path=EXTRAS_DIR / "arch-x11" / "touchpad-workspace-gestures.conf",
        target_path=Path.home() / ".config" / "libinput-gestures.conf",
        requires=("linux", "x11", "xfce"),
    ),
    "arch-x11/lightdm-locale.xprofile": ExtraConfig(
        name="LightDM xprofile locale",
        source_path=EXTRAS_DIR / "arch-x11" / "lightdm-locale.xprofile",
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
    apply_shell_actions.ensure_dir_exists(
        directory=extra.target_path.parent,
        script_name=SCRIPT_NAME,
        dry_run=dry_run,
    )
    apply_shell_actions.create_symlink(
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


def resolve_selected_extras(
    *,
    profile_selected: tuple[str, ...] | None,
    requested: tuple[str, ...],
    include_all: bool,
) -> tuple[str, ...] | None:
    if include_all:
        return None
    if not requested:
        return profile_selected
    get_selected_extras(selected=requested)
    if profile_selected is None:
        return requested
    unavailable = sorted(set(requested) - set(profile_selected))
    if unavailable:
        raise KeyError(
            "Requested extra(s) are not subscribed by the active profile: "
            f"{', '.join(unavailable)}",
        )
    return requested

##
## === PROGRAM MAIN
##


def remove_symlinks(
    *,
    dry_run: bool,
    selected: tuple[str, ...] | None = None,
) -> None:
    log_messages.configure(write_to_file=not dry_run)
    _log_message("Started removing extra config symlinks")
    selected_extras = get_selected_extras(selected=selected)
    for extra in selected_extras.values():
        apply_shell_actions.remove_symlink(
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
    log_messages.configure(write_to_file=not dry_run)
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
    parser.add_argument(
        "--extra",
        action="append",
        choices=sorted(EXTRAS),
        default=[],
        help="Apply one subscribed extra. Can be passed multiple times",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Apply all known extras, ignoring profile extra subscriptions",
    )
    args = parser.parse_args()
    if args.all and args.extra:
        parser.error("--all cannot be combined with --extra")
    profile = load_profiles.load_profile(profile_name=args.profile)
    selected = resolve_selected_extras(
        profile_selected=profile.extras if profile is not None else None,
        requested=tuple(args.extra),
        include_all=args.all,
    )
    run(
        dry_run=args.dry_run,
        selected=selected,
        platform_tags=profile.platforms if profile is not None else None,
    )

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
