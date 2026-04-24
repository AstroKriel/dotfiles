## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from pathlib import Path
from typing import cast

## local
from setup import editors as setup_editors
from setup import extras as setup_extras
from setup import rules as setup_rules
from setup import shell as setup_shell
from setup import tools as setup_tools
from utils import load_profiles
from utils import log_messages

##
## === SCRIPT CONFIG
##

SCRIPT_NAME = Path(__file__).name

_log_message = log_messages.make_logger(SCRIPT_NAME)

##
## === PROFILE VALIDATION
##


def validate_profile(
    *,
    profile: load_profiles.SystemProfile,
) -> bool:
    """Validate profile subscriptions without changing the system."""
    is_valid = True
    known_shells = {shell_config.name for shell_config in setup_shell.SHELLS}
    if profile.shell is not None and profile.shell not in known_shells:
        _log_message(f"Unknown `shell` in `this-system.toml`: `{profile.shell}`")
        is_valid = False
    subscription_groups = [
        ("editor", profile.editors, setup_editors.EDITORS),
        ("tool", profile.tools, setup_tools.TOOLS),
        ("extra", profile.extras, setup_extras.EXTRAS),
    ]
    for subscription_kind, subscribed_keys, available_configs in subscription_groups:
        unknown_subscription_keys = sorted(set(subscribed_keys) - set(available_configs))
        if unknown_subscription_keys:
            _log_message(
                f"Unknown `{subscription_kind}` subscription(s): "
                f"{', '.join(unknown_subscription_keys)}",
            )
            is_valid = False
    for editor_key in profile.editors:
        editor = setup_editors.EDITORS.get(editor_key)
        if editor is None:
            continue
        if not editor.dotfiles_dir.exists():
            _log_message(f"Missing editor source directory: {editor.dotfiles_dir}")
            is_valid = False
        if editor.files is None:
            continue
        for file_name in editor.files:
            modules_dir = editor.dotfiles_dir / file_name
            if not modules_dir.exists():
                _log_message(f"Missing editor module directory: {modules_dir}")
                is_valid = False
    for tool_key in profile.tools:
        tool = setup_tools.TOOLS.get(tool_key)
        if tool is None:
            continue
        if not tool.dotfiles_dir.exists():
            _log_message(f"Missing tool source directory: {tool.dotfiles_dir}")
            is_valid = False
    for extra_key in profile.extras:
        extra = setup_extras.EXTRAS.get(extra_key)
        if extra is None:
            continue
        if not extra.source_path.exists():
            _log_message(f"Missing extra source file: {extra.source_path}")
            is_valid = False
        missing_platform_tags = sorted(set(extra.requires) - set(profile.platforms))
        if missing_platform_tags:
            _log_message(
                f"`extras` subscription `{extra_key}` is missing platform tag(s): "
                f"{', '.join(missing_platform_tags)}",
            )
            is_valid = False
    if is_valid:
        _log_message("Profile validation passed.")
    return is_valid


##
## === PROGRAM MAIN
##


def main():
    parser = argparse.ArgumentParser(
        description="Set up the full dotfiles environment from a system profile.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without applying them",
    )
    parser.add_argument(
        "--remove-symlinks",
        action="store_true",
        help="Remove dotfile symlinks for the selected profile, or all if no profile exists",
    )
    parser.add_argument(
        "--check-profile",
        action="store_true",
        help="Validate profile subscriptions and exit without applying changes",
    )
    args = parser.parse_args()
    dry_run = cast(bool, args.dry_run)
    remove_symlinks = cast(bool, args.remove_symlinks)
    check_profile = cast(bool, args.check_profile)
    log_messages.configure(write_to_file=not (dry_run or check_profile))
    profile = load_profiles.load_profile(
        required=not remove_symlinks,
    )
    if check_profile:
        if profile is None:
            parser.error("`this-system.toml` is required for `--check-profile`")
        if not validate_profile(profile=profile):
            raise SystemExit(1)
        return
    ## no `this-system.toml` means remove all known links
    if remove_symlinks:
        setup_shell.remove_symlinks(
            dry_run=dry_run,
        )
        setup_tools.remove_symlinks(
            dry_run=dry_run,
            tool_keys=profile.tools if profile is not None else None,
        )
        setup_editors.remove_symlinks(
            dry_run=dry_run,
            editor_keys=profile.editors if profile is not None else None,
        )
        setup_extras.remove_symlinks(
            dry_run=dry_run,
            extra_keys=profile.extras if profile is not None else None,
        )
        if profile is None or profile.link_rules:
            setup_rules.remove_symlinks(dry_run=dry_run)
        return
    if profile is None:
        parser.error("`this-system.toml` is required unless `--remove-symlinks` is specified")
    shell_name = profile.shell
    if shell_name is None:
        parser.error(
            "`shell` is missing from `this-system.toml`; "
            'add `shell = "zsh"` or `shell = "bash"`.',
        )
    setup_shell.run(
        shell=shell_name,
        dry_run=dry_run,
    )
    setup_tools.run(
        dry_run=dry_run,
        tool_keys=profile.tools,
    )
    setup_editors.run(
        dry_run=dry_run,
        editor_keys=profile.editors,
    )
    setup_extras.run(
        dry_run=dry_run,
        extra_keys=profile.extras,
        platform_tags=profile.platforms,
    )
    if profile.link_rules:
        setup_rules.run(dry_run=dry_run)


##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
