## { MODULE

##
## === DEPENDENCIES
##

## stdlib
from pathlib import Path

## local
from local_helpers.config_pipeline import config_registry
from local_helpers.config_pipeline import config_spec
from local_helpers.config_pipeline import errors

##
## === CONSTANTS
##

## The group set is explicit, never inferred from the tree (`FUL-1`).
CONFIG_GROUPS = ("tools", "editors", "shell", "extras", "managers", "rules")

##
## === DISCOVER
##


def discover_full_config_registry(
    *,
    configs_root: Path,
) -> config_registry.FullConfigRegistry:
    """
    Scan `configs/<group>/<concept>/_config_spec.toml` and build the registry.

    Pure and deterministic (`FUL-3`): the same tree yields an identical result.
    Every config-spec error and every duplicate key is gathered and reported
    together (`ov#4`); a single fault fails the whole build with no partial
    registry (`FUL-6`). An unknown `needs` target is not checked here; the
    registry only records (`FUL-5`).
    """
    discovered = _scan_concept_dirs(
        configs_root=configs_root,
    )
    collected_errors: list[errors.ConfigPipelineError] = []
    collected_errors.extend(
        _duplicate_key_errors(
            discovered=discovered,
        )
    )
    parsed: dict[config_registry.ConceptKey, config_spec.ConfigSpec] = {}
    for key, concept_dir in discovered:
        try:
            spec = config_spec.load_config_spec(
                concept_dir=concept_dir,
            )
        except errors.ConfigSpecError as error:
            collected_errors.append(error)
            continue
        ## A duplicate key is already reported above; keep the first parse so a
        ## later collision does not overwrite it before the aggregate is raised.
        parsed.setdefault(key, spec)
    if collected_errors:
        raise errors.AggregatedConfigError(
            errors=tuple(collected_errors),
        )
    entries = tuple(sorted(parsed.items(), key=lambda item: item[0]))
    return config_registry.FullConfigRegistry(
        entries=entries,
    )


##
## === SCAN
##


def _scan_concept_dirs(
    *,
    configs_root: Path,
) -> tuple[tuple[config_registry.ConceptKey, Path], ...]:
    """
    Return `(concept_key, concept_dir)` for every concept under a known group.

    Groups are visited in `CONFIG_GROUPS` order and concepts in sorted order,
    so the scan is deterministic; concept directories outside the known group
    set are never seen (`FUL-1`).
    """
    discovered: list[tuple[config_registry.ConceptKey, Path]] = []
    for group in CONFIG_GROUPS:
        group_dir = configs_root / group
        if not group_dir.is_dir():
            continue
        for concept_dir in sorted(group_dir.iterdir()):
            if concept_dir.is_dir():
                discovered.append((concept_dir.name, concept_dir))
    return tuple(discovered)


def _duplicate_key_errors(
    *,
    discovered: tuple[tuple[config_registry.ConceptKey, Path], ...],
) -> tuple[errors.ConfigRegistryError, ...]:
    """Report each `concept_key` that appears under more than one path (`FUL-2`)."""
    paths_by_key: dict[config_registry.ConceptKey, list[Path]] = {}
    for key, concept_dir in discovered:
        paths_by_key.setdefault(key, []).append(concept_dir)
    return tuple(
        errors.ConfigRegistryError(
            concept_key=key,
            paths=tuple(paths),
        )
        for key, paths in paths_by_key.items()
        if len(paths) > 1
    )


## } MODULE
