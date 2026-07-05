## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
import tempfile
import unittest
from pathlib import Path

## local
from local_helpers.config_pipeline import config_registry
from local_helpers.config_pipeline import config_spec
from local_helpers.config_pipeline import serialize_config

##
## === FIXTURES
##

TMUX = """
name = "Tmux"
[check]
command = "tmux"
[[install]]
when = { manager = "pacman" }
pkg  = "tmux"
[[link]]
source = "."
dir    = "~/.config"
name   = "tmux"
mode   = "link"
"""

CONKY = """
name = "Conky"
needs = ["lua", "zathura"]
[[install]]
when = { manager = "pacman" }
pkg  = "conky"
"""

## the canonical serialisation of a minimal one-concept registry, keys sorted.
## pins the on-disk lock format so a change to it is a deliberate, visible diff.
GOLDEN_MINIMAL = """{
  "tmux": {
    "check": null,
    "group": null,
    "installs": [
      {
        "kind": null,
        "pkg": "tmux",
        "when": {
          "manager": "pacman",
          "platform": null
        }
      }
    ],
    "links": [],
    "name": "Tmux",
    "needs": []
  }
}
"""

MINIMAL = """
name = "Tmux"
[[install]]
when = { manager = "pacman" }
pkg  = "tmux"
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


class TestSerialize_RoundTrip(unittest.TestCase):

    def test_full_registry_round_trips(
        self,
    ):
        registry = _make_full_registry(
            test_case=self,
            specs={"tmux": TMUX, "conky": CONKY},
        )
        restored = serialize_config.load_full_config_registry(
            text=serialize_config.dump_full_config_registry(registry=registry),
        )
        ## `FUL-7`: `load(dump(r)) == r`.
        self.assertEqual(
            restored,
            registry,
        )

    def test_filtered_registry_round_trips(
        self,
    ):
        full_registry = _make_full_registry(
            test_case=self,
            specs={"tmux": TMUX, "conky": CONKY},
        )
        filtered = config_registry.FilteredConfigRegistry(entries=full_registry.entries)
        restored = serialize_config.load_filtered_config_registry(
            text=serialize_config.dump_filtered_config_registry(registry=filtered),
        )
        self.assertEqual(
            restored,
            filtered,
        )


class TestSerialize_Canonical(unittest.TestCase):

    def test_minimal_matches_golden(
        self,
    ):
        registry = _make_full_registry(
            test_case=self,
            specs={"tmux": MINIMAL},
        )
        self.assertEqual(
            serialize_config.dump_full_config_registry(registry=registry),
            GOLDEN_MINIMAL,
        )

    def test_dump_is_stable(
        self,
    ):
        registry = _make_full_registry(
            test_case=self,
            specs={"tmux": TMUX, "conky": CONKY},
        )
        ## `FUL-3`: identical input yields byte-identical output.
        self.assertEqual(
            serialize_config.dump_full_config_registry(registry=registry),
            serialize_config.dump_full_config_registry(registry=registry),
        )

    def test_top_level_keys_are_sorted(
        self,
    ):
        registry = _make_full_registry(
            test_case=self,
            specs={"tmux": TMUX, "conky": CONKY},
        )
        text = serialize_config.dump_full_config_registry(registry=registry)
        ## `conky` sorts before `tmux` in the serialised document.
        self.assertLess(
            text.index('"conky"'),
            text.index('"tmux"'),
        )


##
## === ENTRY POINT
##

if __name__ == "__main__":
    unittest.main()

## } U-TEST
