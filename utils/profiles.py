## { MODULE

##
## === DEPENDENCIES
##

## stdlib
from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any

##
## === PROFILE CONFIG
##

DOTFILES_DIR = Path(__file__).resolve().parent.parent
PROFILES_DIR = DOTFILES_DIR / "profiles"
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

##
## === PROFILE HELPERS
##


def load_profile(
    *,
    profile_name: str | None = None,
    required: bool = False,
) -> SystemProfile | None:
    """Load a named profile or the local `this-system.toml` profile."""
    profile_path = resolve_profile_path(profile_name=profile_name)
    if profile_path is None:
        if required:
            raise FileNotFoundError(
                "No system profile found. Create `this-system.toml` or pass `--profile <name>`.",
            )
        return None
    raw_profile = tomllib.loads(profile_path.read_text())
    return create_profile(raw_profile=raw_profile)


def resolve_profile_path(
    *,
    profile_name: str | None,
) -> Path | None:
    """Resolve the profile path from a profile name or `this-system.toml`."""
    if profile_name is not None:
        profile_path = PROFILES_DIR / f"{profile_name}.toml"
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile `{profile_name}` not found at: {profile_path}")
        return profile_path
    if THIS_SYSTEM_PROFILE_PATH.exists() or THIS_SYSTEM_PROFILE_PATH.is_symlink():
        return THIS_SYSTEM_PROFILE_PATH
    return None


def create_profile(
    *,
    raw_profile: dict[str, Any],
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
    )


def _get_optional_string(
    *,
    raw_profile: dict[str, Any],
    key: str,
) -> str | None:
    value = raw_profile.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"`{key}` must be a string when set.")
    return value


def _get_string_tuple(
    *,
    raw_profile: dict[str, Any],
    key: str,
) -> tuple[str, ...]:
    value = raw_profile.get(key, [])
    if not isinstance(value, list):
        raise TypeError(f"`{key}` must be a list of strings.")
    if not all(isinstance(item, str) for item in value):
        raise TypeError(f"`{key}` must contain only strings.")
    return tuple(value)

## } MODULE
