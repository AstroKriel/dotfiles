## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import json
from typing import cast

## local
from local_helpers.config_pipeline import config_registry
from local_helpers.config_pipeline import config_spec

##
## === DUMP
##


def dump_full_config_registry(
    *,
    registry: config_registry.FullConfigRegistry,
) -> str:
    """Serialise the full registry to canonical JSON, keys sorted (`FUL-7`, `ov#18`)."""
    return _dump_entries(
        entries=registry.entries,
    )


def dump_filtered_config_registry(
    *,
    registry: config_registry.FilteredConfigRegistry,
) -> str:
    """Serialise the filtered registry to canonical JSON, keys sorted (`FIL-6`)."""
    return _dump_entries(
        entries=registry.entries,
    )


def _dump_entries(
    *,
    entries: tuple[tuple[config_registry.ConceptKey, config_spec.ConfigSpec], ...],
) -> str:
    """
    Render `concept_key -> ConfigSpec` entries as full-fidelity JSON.

    `sort_keys` makes the output canonical and diffable; a trailing newline
    keeps the tracked lock file POSIX-clean. Serialisation is full fidelity so
    it round-trips (`FUL-7`): every `ConfigSpec` field is emitted.
    """
    document = {key: _spec_to_jsonable(spec=spec) for key, spec in entries}
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def _spec_to_jsonable(
    *,
    spec: config_spec.ConfigSpec,
) -> dict[str, object]:
    return {
        "name": spec.name,
        "check": _check_to_jsonable(check=spec.check),
        "installs": [_install_to_jsonable(install=install) for install in spec.installs],
        "links": [_link_to_jsonable(link=link) for link in spec.links],
        "group": spec.group,
        "needs": list(spec.needs),
    }


def _check_to_jsonable(
    *,
    check: config_spec.Check | None,
) -> dict[str, object] | None:
    if check is None:
        return None
    return {
        "command": check.command,
        "macos_app": check.macos_app,
        "file": check.file,
    }


def _install_to_jsonable(
    *,
    install: config_spec.InstallAvenue,
) -> dict[str, object]:
    return {
        "when": _when_to_jsonable(when=install.when),
        "kind": install.kind,
        "pkg": install.pkg,
    }


def _link_to_jsonable(
    *,
    link: config_spec.Link,
) -> dict[str, object]:
    return {
        "when": _when_to_jsonable(when=link.when),
        "source": link.source,
        "dir": link.dir,
        "name": link.name,
        "mode": link.mode,
    }


def _when_to_jsonable(
    *,
    when: config_spec.When | None,
) -> dict[str, object] | None:
    if when is None:
        return None
    return {
        "platform": when.platform,
        "manager": when.manager,
    }


##
## === LOAD
##


def load_full_config_registry(
    *,
    text: str,
) -> config_registry.FullConfigRegistry:
    """Reconstruct a full registry from its JSON serialisation (`FUL-7`)."""
    return config_registry.FullConfigRegistry(
        entries=_load_entries(text=text),
    )


def load_filtered_config_registry(
    *,
    text: str,
) -> config_registry.FilteredConfigRegistry:
    """Reconstruct a filtered registry from its JSON serialisation."""
    return config_registry.FilteredConfigRegistry(
        entries=_load_entries(text=text),
    )


def _load_entries(
    *,
    text: str,
) -> tuple[tuple[config_registry.ConceptKey, config_spec.ConfigSpec], ...]:
    document = cast(dict[str, object], json.loads(text))
    return tuple(
        sorted(
            (
                (key, _spec_from_jsonable(raw_spec=cast(dict[str, object], raw_spec)))
                for key, raw_spec in document.items()
            ),
            key=lambda item: item[0],
        )
    )


def _spec_from_jsonable(
    *,
    raw_spec: dict[str, object],
) -> config_spec.ConfigSpec:
    return config_spec.ConfigSpec(
        name=cast(str, raw_spec["name"]),
        check=_check_from_jsonable(raw_check=cast("dict[str, object] | None", raw_spec["check"])),
        installs=tuple(
            _install_from_jsonable(raw_install=cast(dict[str, object], raw_install))
            for raw_install in cast(list[object], raw_spec["installs"])
        ),
        links=tuple(
            _link_from_jsonable(raw_link=cast(dict[str, object], raw_link))
            for raw_link in cast(list[object], raw_spec["links"])
        ),
        group=cast("str | None", raw_spec["group"]),
        needs=tuple(cast(list[str], raw_spec["needs"])),
    )


def _check_from_jsonable(
    *,
    raw_check: dict[str, object] | None,
) -> config_spec.Check | None:
    if raw_check is None:
        return None
    return config_spec.Check(
        command=cast("str | None", raw_check["command"]),
        macos_app=cast("str | None", raw_check["macos_app"]),
        file=cast("str | None", raw_check["file"]),
    )


def _install_from_jsonable(
    *,
    raw_install: dict[str, object],
) -> config_spec.InstallAvenue:
    return config_spec.InstallAvenue(
        when=_when_from_jsonable(raw_when=cast("dict[str, object] | None", raw_install["when"])),
        kind=cast("str | None", raw_install["kind"]),
        pkg=cast("str | None", raw_install["pkg"]),
    )


def _link_from_jsonable(
    *,
    raw_link: dict[str, object],
) -> config_spec.Link:
    return config_spec.Link(
        when=_when_from_jsonable(raw_when=cast("dict[str, object] | None", raw_link["when"])),
        source=cast(str, raw_link["source"]),
        dir=cast(str, raw_link["dir"]),
        name=cast(str, raw_link["name"]),
        mode=cast(str, raw_link["mode"]),
    )


def _when_from_jsonable(
    *,
    raw_when: dict[str, object] | None,
) -> config_spec.When | None:
    if raw_when is None:
        return None
    return config_spec.When(
        platform=cast("str | None", raw_when["platform"]),
        manager=cast("str | None", raw_when["manager"]),
    )


## } MODULE
