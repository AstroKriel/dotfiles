## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

## local
from local_helpers.config_pipeline import errors

##
## === CONSTANTS
##

SPEC_FILENAME = "_config_spec.toml"

ALLOWED_WHEN_KEYS = ("platform", "manager")
INSTALL_KINDS = ("config-only", "script")
LINK_MODES = ("link", "copy")

##
## === TYPES
##


@dataclass(frozen=True)
class When:
    """A `[[install]]` or `[[link]]` predicate; keys are a subset of `ALLOWED_WHEN_KEYS`."""

    platform: str | None
    manager: str | None


@dataclass(frozen=True)
class Check:
    """The presence gate; not an action (`ov#6`)."""

    command: str | None
    macos_app: str | None
    file: str | None


@dataclass(frozen=True)
class InstallAvenue:
    """One acceptable way to install; `kind` omitted means a package install."""

    when: When | None
    kind: str | None
    pkg: str | None


@dataclass(frozen=True)
class Link:
    """One link entry; `source` is a filename or `"."` for the whole directory."""

    when: When | None
    source: str
    dir: str
    name: str
    mode: str


@dataclass(frozen=True)
class ConfigSpec:
    """A parsed `_config_spec.toml`; relationships (`needs`, `group`) kept raw."""

    name: str
    check: Check | None
    installs: tuple[InstallAvenue, ...]
    links: tuple[Link, ...]
    group: str | None
    needs: tuple[str, ...]


##
## === PARSE
##


def load_config_spec(
    *,
    concept_dir: Path,
) -> ConfigSpec:
    """
    Load and validate the `_config_spec.toml` in a concept directory.

    Pure and total (`SPEC-8`): reads only the one file, and converts every
    failure into a typed `ConfigSpecError`; it never raises an untyped
    exception.
    """
    spec_path = concept_dir / SPEC_FILENAME
    if not spec_path.is_file():
        raise errors.ConfigSpecMissingError(concept_dir=concept_dir)
    try:
        raw_text = spec_path.read_text()
    except OSError as error:
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="file could not be read",
        ) from error
    try:
        raw_spec = tomllib.loads(raw_text)
    except tomllib.TOMLDecodeError as error:
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="file is not valid TOML",
        ) from error
    return _build_config_spec(
        spec_path=spec_path,
        raw_spec=cast(dict[str, object], raw_spec),
    )


def _build_config_spec(
    *,
    spec_path: Path,
    raw_spec: dict[str, object],
) -> ConfigSpec:
    name = raw_spec.get("name")
    if not isinstance(name, str) or not name.strip():
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="`name` must be a non-empty string",
        )
    raw_installs = raw_spec.get("install", [])
    if not isinstance(raw_installs, list) or len(cast(list[object], raw_installs)) == 0:
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="at least one `[[install]]` is required",
        )
    installs = tuple(
        _build_install(
            spec_path=spec_path,
            raw_install=cast(dict[str, object], raw_install),
        )
        for raw_install in cast(list[object], raw_installs)
    )
    raw_links = raw_spec.get("link", [])
    if not isinstance(raw_links, list):
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="`link` must be a list of tables",
        )
    links = tuple(
        _build_link(
            spec_path=spec_path,
            raw_link=cast(dict[str, object], raw_link),
        )
        for raw_link in cast(list[object], raw_links)
    )
    check = _build_check(
        spec_path=spec_path,
        raw_check=raw_spec.get("check"),
    )
    group = _as_optional_str(
        spec_path=spec_path,
        field="group",
        value=raw_spec.get("group"),
    )
    needs = _as_str_tuple(
        spec_path=spec_path,
        field="needs",
        value=raw_spec.get("needs", []),
    )
    return ConfigSpec(
        name=name,
        check=check,
        installs=installs,
        links=links,
        group=group,
        needs=needs,
    )


def _build_install(
    *,
    spec_path: Path,
    raw_install: dict[str, object],
) -> InstallAvenue:
    kind = raw_install.get("kind")
    if kind is not None and kind not in INSTALL_KINDS:
        allowed = ", ".join(f"`{value}`" for value in INSTALL_KINDS)
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`kind` must be one of {{{allowed}}} when set; got `{kind}`",
        )
    pkg = _as_optional_str(
        spec_path=spec_path,
        field="pkg",
        value=raw_install.get("pkg"),
    )
    has_pkg = pkg is not None
    if kind is None and not has_pkg:
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="a package install requires `pkg`",
        )
    if kind is not None and has_pkg:
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`{kind}` install must not set `pkg`",
        )
    when = _build_when(
        spec_path=spec_path,
        raw_when=raw_install.get("when"),
    )
    return InstallAvenue(
        when=when,
        kind=kind,
        pkg=pkg,
    )


def _build_link(
    *,
    spec_path: Path,
    raw_link: dict[str, object],
) -> Link:
    source = _as_required_str(
        spec_path=spec_path,
        field="link.source",
        value=raw_link.get("source"),
    )
    target_dir = _as_required_str(
        spec_path=spec_path,
        field="link.dir",
        value=raw_link.get("dir"),
    )
    name = _as_required_str(
        spec_path=spec_path,
        field="link.name",
        value=raw_link.get("name"),
    )
    mode = raw_link.get("mode")
    if mode not in LINK_MODES:
        allowed = ", ".join(f"`{value}`" for value in LINK_MODES)
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`link.mode` must be one of {{{allowed}}}; got `{mode}`",
        )
    when = _build_when(
        spec_path=spec_path,
        raw_when=raw_link.get("when"),
    )
    return Link(
        when=when,
        source=source,
        dir=target_dir,
        name=name,
        mode=mode,
    )


def _build_when(
    *,
    spec_path: Path,
    raw_when: object,
) -> When | None:
    if raw_when is None:
        return None
    if not isinstance(raw_when, dict):
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="`when` must be a table",
        )
    when = cast(dict[str, object], raw_when)
    unknown_keys = tuple(key for key in when if key not in ALLOWED_WHEN_KEYS)
    if unknown_keys:
        joined = ", ".join(f"`{key}`" for key in unknown_keys)
        allowed = ", ".join(f"`{key}`" for key in ALLOWED_WHEN_KEYS)
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`when` has unknown key(s): {joined}; allowed: {allowed}",
        )
    return When(
        platform=_as_optional_str(
            spec_path=spec_path,
            field="when.platform",
            value=when.get("platform"),
        ),
        manager=_as_optional_str(
            spec_path=spec_path,
            field="when.manager",
            value=when.get("manager"),
        ),
    )


def _build_check(
    *,
    spec_path: Path,
    raw_check: object,
) -> Check | None:
    if raw_check is None:
        return None
    if not isinstance(raw_check, dict):
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="`[check]` must be a table",
        )
    check = cast(dict[str, object], raw_check)
    command = _as_optional_str(
        spec_path=spec_path,
        field="check.command",
        value=check.get("command"),
    )
    macos_app = _as_optional_str(
        spec_path=spec_path,
        field="check.macos_app",
        value=check.get("macos_app"),
    )
    target_file = _as_optional_str(
        spec_path=spec_path,
        field="check.file",
        value=check.get("file"),
    )
    if command is None and macos_app is None and target_file is None:
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason="`[check]` must set at least one of `command`, `macos_app`, `file`",
        )
    return Check(
        command=command,
        macos_app=macos_app,
        file=target_file,
    )


##
## === FIELD COERCION
##


def _as_required_str(
    *,
    spec_path: Path,
    field: str,
    value: object,
) -> str:
    if not isinstance(value, str) or not value:
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`{field}` must be a non-empty string",
        )
    return value


def _as_optional_str(
    *,
    spec_path: Path,
    field: str,
    value: object,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`{field}` must be a string when set",
        )
    return value


def _as_str_tuple(
    *,
    spec_path: Path,
    field: str,
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`{field}` must be a list of strings",
        )
    items = cast(list[object], value)
    if not all(isinstance(item, str) for item in items):
        raise errors.ConfigSpecSchemaError(
            spec_path=spec_path,
            reason=f"`{field}` must contain only strings",
        )
    return tuple(cast(list[str], items))


## } MODULE
