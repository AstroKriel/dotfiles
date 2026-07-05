## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
import tempfile
import unittest
from pathlib import Path

## local
from local_helpers.config_pipeline import config_spec
from local_helpers.config_pipeline import discover_config
from local_helpers.config_pipeline import errors

##
## === FIXTURES
##

TMUX = """
name = "Tmux"
[[install]]
when = { manager = "pacman" }
pkg  = "tmux"
"""

## Concept-level `needs` with a target that is not itself a concept (`FUL-5`).
CONKY = """
name = "Conky"
needs = ["lua"]
[[install]]
when = { manager = "pacman" }
pkg  = "conky"
"""

BAD_WHEN_KEY = """
name = "Broken"
[[install]]
when = { os = "linux" }
pkg  = "broken"
"""


def _make_configs_root(
    *,
    test_case: unittest.TestCase,
    tree: dict[str, dict[str, str | None]],
) -> Path:
    """
    Build a temporary `configs/` tree from `{group: {concept: body_or_None}}`.

    A `None` body creates the concept directory without a `_config_spec.toml`,
    for the missing-spec case.
    """
    temporary_dir = tempfile.TemporaryDirectory()
    test_case.addCleanup(temporary_dir.cleanup)
    configs_root = Path(temporary_dir.name)
    for group, concepts in tree.items():
        for concept, body in concepts.items():
            concept_dir = configs_root / group / concept
            concept_dir.mkdir(parents=True)
            if body is not None:
                (concept_dir / config_spec.SPEC_FILENAME).write_text(body)
    return configs_root


##
## === TEST SUITE
##


class TestDiscover_Happy(unittest.TestCase):

    def test_two_concepts_across_groups_discovered(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"tmux": TMUX},
                "extras": {"conky": CONKY},
            },
        )
        registry = discover_config.discover_full_config_registry(
            configs_root=configs_root,
        )
        self.assertEqual(
            registry.keys(),
            ("conky", "tmux"),
        )

    def test_keys_are_sorted(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"tmux": TMUX, "conky": CONKY},
            },
        )
        registry = discover_config.discover_full_config_registry(
            configs_root=configs_root,
        )
        self.assertEqual(
            list(registry.keys()),
            sorted(registry.keys()),
        )

    def test_relationships_preserved(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "extras": {"conky": CONKY},
            },
        )
        registry = discover_config.discover_full_config_registry(
            configs_root=configs_root,
        )
        ## `FUL-4`: `needs` recorded, not flattened. `FUL-5`: unknown target kept.
        self.assertEqual(
            registry["conky"].needs,
            ("lua",),
        )

    def test_discovery_is_deterministic(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"tmux": TMUX},
                "extras": {"conky": CONKY},
            },
        )
        first = discover_config.discover_full_config_registry(
            configs_root=configs_root,
        )
        second = discover_config.discover_full_config_registry(
            configs_root=configs_root,
        )
        ## `FUL-3`: same tree yields an equal registry.
        self.assertEqual(
            first,
            second,
        )

    def test_unknown_group_ignored(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"tmux": TMUX},
                "randomgroup": {"conky": CONKY},
            },
        )
        registry = discover_config.discover_full_config_registry(
            configs_root=configs_root,
        )
        ## `FUL-1`: the group set is explicit; `randomgroup` is never scanned.
        self.assertEqual(
            registry.keys(),
            ("tmux",),
        )

    def test_missing_group_dir_is_skipped(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"tmux": TMUX},
            },
        )
        registry = discover_config.discover_full_config_registry(
            configs_root=configs_root,
        )
        self.assertEqual(
            len(registry),
            1,
        )


class TestDiscover_Errors(unittest.TestCase):

    def test_duplicate_key_across_groups_raises(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"fd": TMUX},
                "extras": {"fd": CONKY},
            },
        )
        with self.assertRaises(
            errors.AggregatedConfigError,
        ) as caught:
            discover_config.discover_full_config_registry(
                configs_root=configs_root,
            )
        ## `FUL-2`: the duplicate surfaces as a typed `ConfigRegistryError`.
        self.assertTrue(
            any(
                isinstance(error, errors.ConfigRegistryError)
                for error in caught.exception.errors
            ),
        )

    def test_one_malformed_spec_fails_whole_build(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"tmux": TMUX, "broken": BAD_WHEN_KEY},
            },
        )
        ## `FUL-6`: no partial registry is returned; the build raises.
        with self.assertRaises(
            errors.AggregatedConfigError,
        ):
            discover_config.discover_full_config_registry(
                configs_root=configs_root,
            )

    def test_two_faults_both_reported(
        self,
    ):
        configs_root = _make_configs_root(
            test_case=self,
            tree={
                "tools": {"missing": None},
                "extras": {"broken": BAD_WHEN_KEY},
            },
        )
        with self.assertRaises(
            errors.AggregatedConfigError,
        ) as caught:
            discover_config.discover_full_config_registry(
                configs_root=configs_root,
            )
        ## Aggregation reports every fault before exiting, not just the first.
        self.assertEqual(
            len(caught.exception.errors),
            2,
        )


##
## === ENTRY POINT
##

if __name__ == "__main__":
    unittest.main()

## } U-TEST
