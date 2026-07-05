## { MODULE

##
## === DEPENDENCIES
##

## local
from local_helpers.config_pipeline import config_profile
from local_helpers.config_pipeline import config_registry
from local_helpers.config_pipeline import errors

##
## === FILTER
##


def filter_config_registry(
    *,
    full_registry: config_registry.FullConfigRegistry,
    profile: config_profile.ConfigProfile,
) -> config_registry.FilteredConfigRegistry:
    """
    Restrict the registry to the profile's subscriptions plus their concept
    `needs`-closure (`FIL`).

    Pure and host-free (`FIL-7`): consults no host state and raises only the
    host-free faults `SubscriptionError` (`FIL-2`) and `ChoiceGroupError`
    (`FIL-4`), gathered and reported together (`ov#4`). Bare-package `needs`
    are recorded on their concept, never pulled in as members (`FIL-3`).
    """
    subscriptions = profile.subscriptions
    collected_errors: list[errors.ConfigPipelineError] = []
    unknown_keys = tuple(key for key in subscriptions if key not in full_registry)
    if unknown_keys:
        collected_errors.append(
            errors.SubscriptionError(
                unknown_keys=unknown_keys,
            )
        )
    known_keys = tuple(key for key in subscriptions if key in full_registry)
    collected_errors.extend(
        _find_choice_group_errors(
            subscribed=known_keys,
            full_registry=full_registry,
        )
    )
    if collected_errors:
        raise errors.AggregatedConfigError(
            errors=tuple(collected_errors),
        )
    member_keys = _compute_needs_closure(
        subscribed=subscriptions,
        full_registry=full_registry,
    )
    entries = tuple(
        sorted(
            ((key, full_registry[key]) for key in member_keys),
            key=lambda item: item[0],
        )
    )
    return config_registry.FilteredConfigRegistry(
        entries=entries,
    )


##
## === CLOSURE AND CHOICE GROUPS
##


def _compute_needs_closure(
    *,
    subscribed: tuple[config_registry.ConceptKey, ...],
    full_registry: config_registry.FullConfigRegistry,
) -> set[config_registry.ConceptKey]:
    """
    Grow the subscribed set by following `needs` edges that are themselves
    concepts, recursively (`FIL-3`).

    A `needs` target absent from the registry is a bare package: it stays
    recorded on the concept's `ConfigSpec` and is not added as a member.
    """
    members: set[config_registry.ConceptKey] = set()
    pending = list(subscribed)
    while pending:
        key = pending.pop()
        if key in members:
            continue
        members.add(key)
        for need in full_registry[key].needs:
            if need in full_registry and need not in members:
                pending.append(need)
    return members


def _find_choice_group_errors(
    *,
    subscribed: tuple[config_registry.ConceptKey, ...],
    full_registry: config_registry.FullConfigRegistry,
) -> tuple[errors.ChoiceGroupError, ...]:
    """Report each choice `group` with more than one subscribed member (`FIL-4`)."""
    members_by_group: dict[str, list[config_registry.ConceptKey]] = {}
    for key in subscribed:
        group = full_registry[key].group
        if group is not None:
            members_by_group.setdefault(group, []).append(key)
    return tuple(
        errors.ChoiceGroupError(
            group=group,
            members=tuple(sorted(members)),
        )
        for group, members in sorted(members_by_group.items())
        if len(members) > 1
    )


## } MODULE
