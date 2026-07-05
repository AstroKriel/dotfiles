## { MODULE

##
## === DEPENDENCIES
##

## stdlib
from dataclasses import dataclass

## local
from local_helpers.config_pipeline import config_registry

##
## === TYPES
##


@dataclass(frozen=True)
class ConfigProfile:
    """
    A profile's subscription intent (`FIL-1`): the concept keys it opts into.

    The lists are grouped only for readability in the source TOML; the filter
    unions them into one subscription set. Choice-group membership is not read
    from these lists, it comes from each `ConfigSpec.group` (`FIL-4`). This is
    the pipeline-native profile; migrating the legacy `SystemProfile` (extras
    as file paths, scalar `shell`, no `managers`) is deferred (`overview.md`).
    """

    tools: tuple[str, ...] = ()
    editors: tuple[str, ...] = ()
    extras: tuple[str, ...] = ()
    shell: tuple[str, ...] = ()
    managers: tuple[str, ...] = ()

    @property
    def subscriptions(
        self,
    ) -> tuple[config_registry.ConceptKey, ...]:
        """Every subscribed concept key, de-duplicated and sorted for determinism."""
        merged = (
            *self.tools,
            *self.editors,
            *self.extras,
            *self.shell,
            *self.managers,
        )
        return tuple(sorted(set(merged)))


## } MODULE
