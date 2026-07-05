## { MODULE

##
## === DEPENDENCIES
##

## stdlib
from dataclasses import dataclass
from typing import TypeAlias

## local
from local_helpers.config_pipeline import config_spec

##
## === TYPE ALIASES
##

ConceptKey: TypeAlias = str

##
## === TYPES
##


@dataclass(frozen=True)
class _ConfigRegistry:
    """
    Read-only, mapping-like access over sorted `concept_key -> ConfigSpec`
    entries, shared by the full and filtered registries so they present the
    same interface (`FIL-5`: a filtered registry is a subset, not a new shape).
    """

    entries: tuple[tuple[ConceptKey, config_spec.ConfigSpec], ...]

    def keys(
        self,
    ) -> tuple[ConceptKey, ...]:
        return tuple(key for key, _ in self.entries)

    def as_map(
        self,
    ) -> dict[ConceptKey, config_spec.ConfigSpec]:
        return {key: spec for key, spec in self.entries}

    def __contains__(
        self,
        key: object,
    ) -> bool:
        return any(key == existing for existing, _ in self.entries)

    def __getitem__(
        self,
        key: ConceptKey,
    ) -> config_spec.ConfigSpec:
        for existing, spec in self.entries:
            if existing == key:
                return spec
        raise KeyError(key)

    def __len__(
        self,
    ) -> int:
        return len(self.entries)


@dataclass(frozen=True)
class FullConfigRegistry(_ConfigRegistry):
    """
    The whole `configs/` tree as a `concept_key -> ConfigSpec` map (`FUL`).

    Keys are unique across groups (`FUL-2`) and `entries` are stored sorted by
    key, so the registry is a deterministic function of the tree (`FUL-3`).
    Relationships (`needs`, `group`) live on each `ConfigSpec`, kept raw
    (`FUL-4`, `FUL-5`); this type does not flatten them.
    """


@dataclass(frozen=True)
class FilteredConfigRegistry(_ConfigRegistry):
    """
    A `FullConfigRegistry` restricted to a profile's subscriptions plus their
    `needs`-closure over concepts (`FIL`).

    Structurally identical to `FullConfigRegistry`: a strict subset with
    relationships intact (`FIL-5`), entries sorted by key (`FIL-6`).
    """


## } MODULE
