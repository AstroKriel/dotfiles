## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
import tempfile
import unittest
from pathlib import Path

## local
from local_helpers.config_pipeline import config_profile
from local_helpers.config_pipeline import config_registry
from local_helpers.config_pipeline import config_spec
from local_helpers.config_pipeline import errors
from local_helpers.config_pipeline import filter_config

##
## === FIXTURES
##

TMUX = """
name = "Tmux"
[[install]]
when = { manager = "pacman" }
pkg  = "tmux"
"""

## `conky` needs a bare package (`lua`) and a concept (`zathura`) (`FIL-3`).
CONKY = """
name = "Conky"
needs = ["lua", "zathura"]
[[install]]
when = { manager = "pacman" }
pkg  = "conky"
"""

ZATHURA = """
name = "Zathura"
[[install]]
when = { manager = "pacman" }
pkg  = "zathura"
"""

SHELL_BASH = """
name = "Bash"
group = "shell"
[[install]]
when = { manager = "pacman" }
pkg  = "bash"
"""

SHELL_ZSH = """
name = "Zsh"
group = "shell"
[[install]]
when = { manager = "pacman" }
pkg  = "zsh"
"""


def _make_full_registry(
    *,
    test_case: unittest.TestCase,
    specs: dict[str, str],
) -> config_registry.FullConfigRegistry:
    """Build a `FullConfigRegistry` by parsing each `{key: toml_body}` into a spec."""
    temporary_dir = tempfile.TemporaryDirectory()
    test_case.addCleanup(temporary_dir.cleanup)
    root = Path(temporary_dir.name)
    entries: list[tuple[str, config_spec.ConfigSpec]] = []
    for key, body in sorted(specs.items()):
        concept_dir = root / key
        concept_dir.mkdir()
        (concept_dir / config_spec.SPEC_FILENAME).write_text(body)
        entries.append(
            (
                key,
                config_spec.load_config_spec(
                    concept_dir=concept_dir,
                ),
            )
        )
    return config_registry.FullConfigRegistry(
        entries=tuple(entries),
    )


##
## === TEST SUITE
##


class TestFilter_Membership(unittest.TestCase):

    def test_subscribed_key_kept(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"tmux": TMUX, "zathura": ZATHURA},
        )
        filtered = filter_config.filter_config_registry(
            full_registry=full_registry,
            profile=config_profile.ConfigProfile(tools=("tmux",)),
        )
        ## `FIL-5`: a strict subset of the full registry.
        self.assertEqual(
            filtered.keys(),
            ("tmux",),
        )

    def test_needs_closure_pulls_concepts_not_packages(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"conky": CONKY, "zathura": ZATHURA},
        )
        filtered = filter_config.filter_config_registry(
            full_registry=full_registry,
            profile=config_profile.ConfigProfile(extras=("conky",)),
        )
        ## `FIL-3`: `zathura` (a concept) is pulled in; `lua` (bare package) is not.
        self.assertEqual(
            filtered.keys(),
            ("conky", "zathura"),
        )

    def test_relationships_preserved(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"conky": CONKY, "zathura": ZATHURA},
        )
        filtered = filter_config.filter_config_registry(
            full_registry=full_registry,
            profile=config_profile.ConfigProfile(extras=("conky",)),
        )
        ## `FIL-5`: `needs` survives on the subset, bare package included.
        self.assertEqual(
            filtered["conky"].needs,
            ("lua", "zathura"),
        )

    def test_single_group_member_ok(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"shell-bash": SHELL_BASH, "shell-zsh": SHELL_ZSH},
        )
        filtered = filter_config.filter_config_registry(
            full_registry=full_registry,
            profile=config_profile.ConfigProfile(shell=("shell-zsh",)),
        )
        self.assertEqual(
            filtered.keys(),
            ("shell-zsh",),
        )


class TestFilter_Properties(unittest.TestCase):

    def test_filter_is_deterministic(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"conky": CONKY, "zathura": ZATHURA},
        )
        profile = config_profile.ConfigProfile(extras=("conky",))
        first = filter_config.filter_config_registry(
            full_registry=full_registry,
            profile=profile,
        )
        second = filter_config.filter_config_registry(
            full_registry=full_registry,
            profile=profile,
        )
        ## `FIL-6`: pure and deterministic given `(full_registry, profile)`.
        self.assertEqual(
            first,
            second,
        )

    def test_filter_is_idempotent(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"conky": CONKY, "zathura": ZATHURA},
        )
        once = filter_config.filter_config_registry(
            full_registry=full_registry,
            profile=config_profile.ConfigProfile(extras=("conky",)),
        )
        ## Re-filtering the result (subscribing all its keys) yields the same set.
        again_full = config_registry.FullConfigRegistry(entries=once.entries)
        again = filter_config.filter_config_registry(
            full_registry=again_full,
            profile=config_profile.ConfigProfile(extras=once.keys()),
        )
        self.assertEqual(
            once.entries,
            again.entries,
        )


class TestFilter_Errors(unittest.TestCase):

    def test_unknown_subscription_raises(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"tmux": TMUX},
        )
        with self.assertRaises(
            errors.AggregatedConfigError,
        ) as caught:
            filter_config.filter_config_registry(
                full_registry=full_registry,
                profile=config_profile.ConfigProfile(tools=("nope",)),
            )
        ## `FIL-2`: absent subscriptions surface as a typed `SubscriptionError`.
        self.assertTrue(
            any(
                isinstance(error, errors.SubscriptionError)
                for error in caught.exception.errors
            ),
        )

    def test_choice_group_collision_raises(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"shell-bash": SHELL_BASH, "shell-zsh": SHELL_ZSH},
        )
        with self.assertRaises(
            errors.AggregatedConfigError,
        ) as caught:
            filter_config.filter_config_registry(
                full_registry=full_registry,
                profile=config_profile.ConfigProfile(shell=("shell-bash", "shell-zsh")),
            )
        ## `FIL-4`: two subscribed members of one group is a `ChoiceGroupError`.
        self.assertTrue(
            any(
                isinstance(error, errors.ChoiceGroupError)
                for error in caught.exception.errors
            ),
        )


##
## === ENTRY POINT
##

if __name__ == "__main__":
    unittest.main()

## } U-TEST
