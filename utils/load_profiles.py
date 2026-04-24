## { MODULE

##
## === DEPENDENCIES
##

## stdlib
from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import cast

##
## === PROFILE CONFIG
##

DOTFILES_DIR = Path(__file__).resolve().parent.parent
THIS_SYSTEM_PROFILE_PATH = DOTFILES_DIR / "this-system.toml"

##
## === PROFILE TYPES
##


@dataclass(frozen=True)
class SystemProfile:
    """Selected configuration groups for one system."""

    shell: str | None
    platforms: tuple[str, ...]
    editors: tuple[str, ...]
    tools: tuple[str, ...]
    extras: tuple[str, ...]
    link_rules: bool

##
## === PROFILE HELPERS
##


def load_profile(
    *,
    required: bool = False,
) -> SystemProfile | None:
    """Load the local `this-system.toml` profile."""
    profile_path = resolve_profile_path()
    if profile_path is None:
        if required:
            raise FileNotFoundError(
                "No system profile found. Create `this-system.toml` from a tracked profile.",
            )
        return None
    raw_profile = cast(dict[str, object], tomllib.loads(profile_path.read_text()))
    return create_profile(raw_profile=raw_profile)


def resolve_profile_path() -> Path | None:
    """Resolve the local `this-system.toml` profile path."""
    if THIS_SYSTEM_PROFILE_PATH.exists() or THIS_SYSTEM_PROFILE_PATH.is_symlink():
        return THIS_SYSTEM_PROFILE_PATH
    return None


def create_profile(
    *,
    raw_profile: dict[str, object],
) -> SystemProfile:
    """Create a typed system profile from parsed TOML data."""
    return SystemProfile(
        shell=_get_optional_string(
            raw_profile=raw_profile,
            key="shell",
        ),
        platforms=_get_string_tuple(
            raw_profile=raw_profile,
            key="platforms",
        ),
        editors=_get_string_tuple(
            raw_profile=raw_profile,
            key="editors",
        ),
        tools=_get_string_tuple(
            raw_profile=raw_profile,
            key="tools",
        ),
        extras=_get_string_tuple(
            raw_profile=raw_profile,
            key="extras",
        ),
        link_rules=_get_bool(
            raw_profile=raw_profile,
            key="link_rules",
            default=False,
        ),
    )


def _get_optional_string(
    *,
    raw_profile: dict[str, object],
    key: str,
) -> str | None:
    value = raw_profile.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"`{key}` must be a string when set.")
    return value


def _get_bool(
    *,
    raw_profile: dict[str, object],
    key: str,
    default: bool,
) -> bool:
    value = raw_profile.get(key, default)
    if not isinstance(value, bool):
        raise TypeError(f"`{key}` must be a boolean when set.")
    return value


def _get_string_tuple(
    *,
    raw_profile: dict[str, object],
    key: str,
) -> tuple[str, ...]:
    value = raw_profile.get(key, [])
    if not isinstance(value, list):
        raise TypeError(f"`{key}` must be a list of strings.")
    value_items = cast(list[object], value)
    if not all(isinstance(item, str) for item in value_items):
        raise TypeError(f"`{key}` must contain only strings.")
    return tuple(cast(list[str], value_items))

## } MODULE
