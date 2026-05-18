## { MODULE

##
## === DEPENDENCIES
##

## stdlib
from pathlib import Path

##
## === BASE
##


class ConfigPipelineError(Exception):
    """Base for every typed error raised by the config pipeline."""


class AggregatedConfigError(ConfigPipelineError):
    """
    Several pipeline errors collected and reported together.

    The pipeline never stops at the first failure; it gathers every error it
    can find before raising this (plan-first accountability, `ov#4`).
    """

    def __init__(
        self,
        *,
        errors: tuple[ConfigPipelineError, ...],
    ) -> None:
        self.errors: tuple[ConfigPipelineError, ...] = errors
        joined = "\n".join(f"  - {error}" for error in errors)
        super().__init__(f"config pipeline found {len(errors)} error(s):\n{joined}")


##
## === CONFIG SPEC ERRORS
##


class ConfigSpecError(ConfigPipelineError):
    """Base for problems with a single `_config_spec.toml`."""


class ConfigSpecMissingError(ConfigSpecError):
    """A concept directory has no `_config_spec.toml` (`SPEC-1`)."""

    def __init__(
        self,
        *,
        concept_dir: Path,
    ) -> None:
        self.concept_dir: Path = concept_dir
        super().__init__(f"`_config_spec.toml` not found; searched in {concept_dir}.")


class ConfigSpecSchemaError(ConfigSpecError):
    """A `_config_spec.toml` parsed but violates the schema (`SPEC-2` to `SPEC-5`)."""

    def __init__(
        self,
        *,
        spec_path: Path,
        reason: str,
    ) -> None:
        self.spec_path: Path = spec_path
        self.reason: str = reason
        super().__init__(f"config spec error: {spec_path}: {reason}.")


##
## === REGISTRY AND RESOLUTION ERRORS
##


class ConfigRegistryError(ConfigPipelineError):
    """Two concepts collide on one `concept_key` (`FUL-2`)."""

    def __init__(
        self,
        *,
        concept_key: str,
        paths: tuple[Path, ...],
    ) -> None:
        self.concept_key: str = concept_key
        self.paths: tuple[Path, ...] = paths
        searched = ", ".join(str(path) for path in paths)
        super().__init__(f"duplicate concept key: `{concept_key}`; found in {searched}.")


class SubscriptionError(ConfigPipelineError):
    """A profile subscribes to keys absent from the registry (`FIL-2`)."""

    def __init__(
        self,
        *,
        unknown_keys: tuple[str, ...],
    ) -> None:
        self.unknown_keys: tuple[str, ...] = unknown_keys
        joined = ", ".join(f"`{key}`" for key in unknown_keys)
        super().__init__(f"unknown subscription(s): {joined}.")


class ChoiceGroupError(ConfigPipelineError):
    """More than one subscribed concept shares a choice `group` (`FIL-4`)."""

    def __init__(
        self,
        *,
        group: str,
        members: tuple[str, ...],
    ) -> None:
        self.group: str = group
        self.members: tuple[str, ...] = members
        joined = ", ".join(f"`{member}`" for member in members)
        super().__init__(f"choice group `{group}` has more than one subscribed member; got {joined}.")


class ResolutionError(ConfigPipelineError):
    """One or more subscribed concepts cannot resolve to a `config_plan`."""

    def __init__(
        self,
        *,
        causes: tuple[str, ...],
    ) -> None:
        self.causes: tuple[str, ...] = causes
        joined = "\n".join(f"  - {cause}" for cause in causes)
        super().__init__(f"resolution failed with {len(causes)} cause(s):\n{joined}")


## } MODULE
