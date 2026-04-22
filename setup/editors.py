## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from dataclasses import dataclass
from enum import Enum, auto
import json
from pathlib import Path
import re
import shutil
import sys

## local
from utils import load_profiles
from utils import log_messages, apply_shell_actions

##
## === EDITOR CONFIG
##

SCRIPT_NAME = Path(__file__).name
HOME_DIR = Path.home()
ROOT_DIR = Path(__file__).resolve().parent.parent
DOTFILES_DIR = ROOT_DIR / "editors"
CONFIG_DIR = HOME_DIR / ".config"

_log_message = log_messages.make_logger(SCRIPT_NAME)

_VSCODE_TARGET_DIR = (
    Path.home() / "Library/Application Support/Code/User"
    if sys.platform == "darwin"
    else Path.home() / ".config/Code/User"
)


class PostSetup(Enum):
    DOOM_SYNC = auto()


@dataclass
class RepoConfig:
    name: str
    url: str
    output: Path


@dataclass
class EditorConfig:
    name: str
    command: str
    brew: str
    dotfiles_dir: Path
    target_dir: Path
    files: dict[str, str] | None = None
    extensions: Path | None = None
    mac_app: str | None = None
    clone_repo: RepoConfig | None = None
    post_setup: PostSetup | None = None


EDITORS: dict[str, EditorConfig] = {
    "vscode": EditorConfig(
        name="Visual Studio Code",
        command="code",
        brew="visual-studio-code --cask",
        dotfiles_dir=DOTFILES_DIR / "vscode",
        target_dir=_VSCODE_TARGET_DIR,
        files={
            "settings": "dict",
            "keybindings": "list",
        },
        extensions=DOTFILES_DIR / "vscode" / "extensions.txt",
    ),
    "nvim": EditorConfig(
        name="Neovim",
        command="nvim",
        brew="neovim",
        dotfiles_dir=DOTFILES_DIR / "nvim",
        target_dir=CONFIG_DIR / "nvim",
    ),
    "emacs": EditorConfig(
        name="Emacs (GUI)",
        command="emacs",
        brew="emacs --cask",
        mac_app="Emacs.app",
        dotfiles_dir=DOTFILES_DIR / "emacs",
        target_dir=HOME_DIR / ".doom.d",
        clone_repo=RepoConfig(
            name="Doom-Emacs",
            url="https://github.com/doomemacs/doomemacs",
            output=CONFIG_DIR / "emacs",
        ),
        post_setup=PostSetup.DOOM_SYNC,
    ),
    "zed": EditorConfig(
        name="Zed",
        command="zed" if sys.platform == "darwin" else "zeditor",
        brew="zed --cask",
        dotfiles_dir=DOTFILES_DIR / "zed",
        target_dir=Path.home() / ".config/zed/",
        files={
            "settings": "dict",
            "keymap": "list",
        },
    ),
}

##
## === EDITOR HELPERS
##


def filter_jsonc_comments(
    content: str,
) -> str:
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)  # remove block comments
    content = re.sub(r'//[^\n\r]*', '', content)  # remove line comments
    return content


def merge_config_modules(
    *,
    modules_dir: Path,
    mode: str,
) -> dict | list:
    if mode == "dict":
        merged = {}
    elif mode == "list":
        merged = []
    else:
        _log_message(f"Error: Unsupported mode `{mode}`")
        return None
    if not modules_dir.exists():
        _log_message(f"Skipping. No module directory found: {modules_dir}")
        return None
    for module in sorted(modules_dir.glob("*.jsonc")):
        with module.open("r", encoding="utf-8") as f:
            raw_content = f.read()
            filtered_content = filter_jsonc_comments(raw_content)
            content = json.loads(filtered_content)
            if mode == "dict":
                merged.update(content)
            elif mode == "list":
                merged.extend(content)
    return merged


def install_extensions(
    *,
    command: str,
    extensions_file: Path,
    dry_run: bool,
):
    if not extensions_file.exists():
        _log_message(f"No extensions file found at: {extensions_file}")
        return
    extensions = [e for e in extensions_file.read_text().splitlines() if e.strip()]
    for ext in extensions:
        apply_shell_actions.run_command(
            args=[command, "--install-extension", ext],
            script_name=SCRIPT_NAME,
            description=f"install extension: {ext}",
            dry_run=dry_run,
        )


def shallow_clone_repo(
    *,
    repo: RepoConfig,
    dry_run: bool,
) -> None:
    if repo.output.exists():
        _log_message(f"{repo.name} already exists under: {repo.output}")
        return
    apply_shell_actions.run_command(
        args=["git", "clone", "--depth", "1", repo.url, str(repo.output)],
        script_name=SCRIPT_NAME,
        description=f"clone {repo.name} (shallow) under {repo.output}",
        dry_run=dry_run,
    )


def run_doom_sync(
    *,
    dry_run: bool,
) -> None:
    doom_bin = CONFIG_DIR / "emacs" / "bin" / "doom"
    if not doom_bin.exists():
        _log_message(f"Doom binary not found at: {doom_bin}")
        return
    apply_shell_actions.run_command(
        args=[str(doom_bin), "sync"],
        script_name=SCRIPT_NAME,
        description="doom sync",
        dry_run=dry_run,
        capture_output=False,
    )


def setup_editor(
    *,
    editor: EditorConfig,
    dry_run: bool,
):
    _log_message(f"Started setting up {editor.name}")
    ## check whether the editor is installed
    found_via_app = (
        sys.platform == "darwin"
        and editor.mac_app is not None
        and (Path("/Applications") / editor.mac_app).exists()
    )
    if shutil.which(editor.command) or found_via_app:
        _log_message(f"Found {editor.name} ({editor.command}) in your `$PATH`.")
    else:
        _log_message(
            f"{editor.command} was not found in your `$PATH`.\n"
            f"Install it via: `brew install {editor.brew}`",
        )
        return
    if editor.files is None:
        apply_shell_actions.ensure_dir_exists(
            directory=editor.target_dir.parent,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
        apply_shell_actions.create_symlink(
            source_path=editor.dotfiles_dir,
            target_path=editor.target_dir,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    else:
        setup_editor_files(
            editor=editor,
            dry_run=dry_run,
        )
    if editor.clone_repo is not None:
        shallow_clone_repo(
            repo=editor.clone_repo,
            dry_run=dry_run,
        )
    if editor.post_setup == PostSetup.DOOM_SYNC:
        run_doom_sync(dry_run=dry_run)
    ## install extensions if defined
    if editor.extensions is not None:
        install_extensions(
            command=editor.command,
            extensions_file=editor.extensions,
            dry_run=dry_run,
        )


def setup_editor_files(
    *,
    editor: EditorConfig,
    dry_run: bool,
) -> None:
    if editor.files is None:
        return
    for file_name, mode in editor.files.items():
        modules_dir = editor.dotfiles_dir / file_name
        merged_config = merge_config_modules(
            modules_dir=modules_dir,
            mode=mode,
        )
        if merged_config is None:
            return
        output_path = editor.dotfiles_dir / f"{file_name}.json"
        target_path = editor.target_dir / f"{file_name}.json"
        if dry_run:
            _log_message(f"[dry-run] Would write merged settings to: {output_path}")
        else:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(merged_config, f, indent=2)
            _log_message(f"Wrote merged config to: {output_path}")
        ## ensure target directory exists
        apply_shell_actions.ensure_dir_exists(
            directory=editor.target_dir,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
        ## symlink merged config
        apply_shell_actions.create_symlink(
            source_path=output_path,
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )


def get_selected_editors(
    *,
    editor_keys: tuple[str, ...] | None,
) -> dict[str, EditorConfig]:
    """Return editor configs selected by the active system profile."""
    if editor_keys is None:
        return EDITORS
    unknown_editor_keys = sorted(set(editor_keys) - set(EDITORS))
    if unknown_editor_keys:
        raise KeyError(f"Unknown editor(s): {', '.join(unknown_editor_keys)}")
    return {
        editor_key: EDITORS[editor_key]
        for editor_key in editor_keys
    }


def resolve_selected_editors(
    *,
    subscribed_editor_keys: tuple[str, ...] | None,
    requested_editor_keys: tuple[str, ...],
    include_all: bool,
) -> tuple[str, ...] | None:
    if include_all:
        return None
    if not requested_editor_keys:
        return subscribed_editor_keys
    get_selected_editors(editor_keys=requested_editor_keys)
    if subscribed_editor_keys is None:
        return requested_editor_keys
    unsubscribed_editor_keys = sorted(set(requested_editor_keys) - set(subscribed_editor_keys))
    if unsubscribed_editor_keys:
        raise KeyError(
            "Requested editor(s) are not subscribed by the active profile: "
            f"{', '.join(unsubscribed_editor_keys)}",
        )
    return requested_editor_keys

##
## === PROGRAM MAIN
##


def remove_symlinks(
    *,
    dry_run: bool,
    editor_keys: tuple[str, ...] | None = None,
):
    log_messages.configure(write_to_file=not dry_run)
    _log_message("Started removing editor config symlinks")
    selected_editor_configs = get_selected_editors(editor_keys=editor_keys)
    for editor in selected_editor_configs.values():
        if editor.files is None:
            apply_shell_actions.remove_symlink(
                target_path=editor.target_dir,
                script_name=SCRIPT_NAME,
                dry_run=dry_run,
            )
        else:
            for file_name in editor.files:
                apply_shell_actions.remove_symlink(
                    target_path=editor.target_dir / f"{file_name}.json",
                    script_name=SCRIPT_NAME,
                    dry_run=dry_run,
                )
    _log_message("Finished removing editor config symlinks")


def run(
    *,
    dry_run: bool,
    editor_keys: tuple[str, ...] | None = None,
):
    log_messages.configure(write_to_file=not dry_run)
    selected_editor_configs = get_selected_editors(editor_keys=editor_keys)
    for editor in selected_editor_configs.values():
        setup_editor(
            editor=editor,
            dry_run=dry_run,
        )
    _log_message("Finished setting up editors.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate and symlink subscribed editor settings.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without applying them",
    )
    parser.add_argument(
        "--profile",
        help="Load selected editors from profiles/<name>.toml",
    )
    parser.add_argument(
        "--editor",
        action="append",
        choices=sorted(EDITORS),
        default=[],
        help="Apply one subscribed editor. Can be passed multiple times",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Apply all known editors, ignoring profile editor subscriptions",
    )
    args = parser.parse_args()
    if args.all and args.editor:
        parser.error("--all cannot be combined with --editor")
    profile = load_profiles.load_profile(profile_name=args.profile)
    editor_keys = resolve_selected_editors(
        subscribed_editor_keys=profile.editors if profile is not None else None,
        requested_editor_keys=tuple(args.editor),
        include_all=args.all,
    )
    run(
        dry_run=args.dry_run,
        editor_keys=editor_keys,
    )

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
