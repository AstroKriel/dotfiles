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
from local_helpers.config_pipeline import errors

##
## === FIXTURES
##

VALID_MINIMAL = """
name = "Tmux"
[[install]]
when = { manager = "brew" }
pkg  = "tmux"
"""


def _make_concept_dir(
    *,
    test_case: unittest.TestCase,
    body: str | None,
) -> Path:
    """Create a temporary concept directory; write `_config_spec.toml` iff `body` is set."""
    temporary_dir = tempfile.TemporaryDirectory()
    test_case.addCleanup(temporary_dir.cleanup)
    concept_dir = Path(temporary_dir.name)
    if body is not None:
        (concept_dir / config_spec.SPEC_FILENAME).write_text(body)
    return concept_dir


##
## === TEST SUITE
##


class TestConfigSpec_Required(unittest.TestCase):

    def test_missing_file_raises_missing_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body=None,
        )
        with self.assertRaises(
            errors.ConfigSpecMissingError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_minimal_spec_parses(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body=VALID_MINIMAL,
        )
        spec = config_spec.load_config_spec(
            concept_dir=concept_dir,
        )
        self.assertEqual(
            spec.name,
            "Tmux",
        )
        self.assertEqual(
            len(spec.installs),
            1,
        )

    def test_blank_name_raises_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "  "\n[[install]]\npkg = "x"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_no_install_raises_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "Tmux"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )


class TestConfigSpec_Install(unittest.TestCase):

    def test_package_install_requires_pkg(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nwhen = { manager = "brew" }\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_config_only_forbids_pkg(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nkind = "config-only"\npkg = "x"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_config_only_without_pkg_parses(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nkind = "config-only"\n',
        )
        spec = config_spec.load_config_spec(
            concept_dir=concept_dir,
        )
        self.assertEqual(
            spec.installs[0].kind,
            "config-only",
        )

    def test_unknown_kind_raises_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nkind = "brew-cask"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )


class TestConfigSpec_When(unittest.TestCase):

    def test_unknown_when_key_raises_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nwhen = { platform = "macos", arch = "arm64" }\npkg = "x"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_allowed_when_keys_parse(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nwhen = { platform = "macos", manager = "brew" }\npkg = "x"\n',
        )
        spec = config_spec.load_config_spec(
            concept_dir=concept_dir,
        )
        self.assertEqual(
            spec.installs[0].when,
            config_spec.When(platform="macos", manager="brew"),
        )


class TestConfigSpec_Link(unittest.TestCase):

    def test_link_missing_field_raises_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nkind = "config-only"\n[[link]]\nsource = "f"\ndir = "~"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_bad_link_mode_raises_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nkind = "config-only"\n[[link]]\nsource = "f"\ndir = "~"\nname = ".f"\nmode = "hardlink"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_valid_link_parses(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\n[[install]]\nkind = "config-only"\n[[link]]\nsource = "f"\ndir = "~"\nname = ".f"\nmode = "link"\n',
        )
        spec = config_spec.load_config_spec(
            concept_dir=concept_dir,
        )
        self.assertEqual(
            spec.links[0],
            config_spec.Link(when=None, source="f", dir="~", name=".f", mode="link"),
        )


class TestConfigSpec_Misc(unittest.TestCase):

    def test_needs_kept_raw(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "Conky"\nneeds = ["lua", "zathura"]\n[[install]]\npkg = "conky"\n',
        )
        spec = config_spec.load_config_spec(
            concept_dir=concept_dir,
        )
        self.assertEqual(
            spec.needs,
            ("lua", "zathura"),
        )

    def test_needs_mixed_types_raise_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\nneeds = ["lua", 1]\n[[install]]\npkg = "x"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_group_must_be_string(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X"\ngroup = 3\n[[install]]\npkg = "x"\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )

    def test_invalid_toml_raises_typed_schema_error(
        self,
    ):
        concept_dir = _make_concept_dir(
            test_case=self,
            body='name = "X\n[[install]]\n',
        )
        with self.assertRaises(
            errors.ConfigSpecSchemaError,
        ):
            config_spec.load_config_spec(
                concept_dir=concept_dir,
            )


##
## === ENTRY POINT
##

if __name__ == "__main__":
    unittest.main()

## } U-TEST
