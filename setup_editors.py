## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import sys

## local
from utils import profiles
from utils import logging, shell_actions

##
## === EDITOR CONFIG
##

SCRIPT_NAME = Path(__file__).name
DOTFILES_DIR = Path(__file__).resolve().parent / "editors"

_log_message = logging.make_logger(SCRIPT_NAME)

_VSCODE_TARGET_DIR = (
    Path.home() / "Library/Application Support/Code/User"
    if sys.platform == "darwin"
    else Path.home() / ".config/Code/User"
)


@dataclass
class EditorConfig:
    name: str
    command: str
    brew: str
    dotfiles_dir: Path
    target_dir: Path
    files: dict[str, str]
    extensions: Path | None = None


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
        shell_actions.run_command(
            args=[command, "--install-extension", ext],
            script_name=SCRIPT_NAME,
            description=f"install extension: {ext}",
            dry_run=dry_run,
        )


def setup_editor(
    *,
    editor: EditorConfig,
    dry_run: bool,
):
    _log_message(f"Started setting up {editor.name}")
    ## check whether the editor is installed
    if shutil.which(editor.command):
        _log_message(f"Found {editor.name} ({editor.command}) in your `$PATH`.")
    else:
        _log_message(
            f"{editor.command} was not found in your `$PATH`.\n"
            f"Install it via: `brew install {editor.brew}`",
        )
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
        shell_actions.ensure_dir_exists(
            directory=editor.target_dir,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
        ## symlink merged config
        shell_actions.create_symlink(
            source_path=output_path,
            target_path=target_path,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    ## install extensions if defined
    if editor.extensions is not None:
        install_extensions(
            command=editor.command,
            extensions_file=editor.extensions,
            dry_run=dry_run,
        )


def get_selected_editors(
    *,
    selected: tuple[str, ...] | None,
) -> dict[str, EditorConfig]:
    """Return editor configs selected by the active system profile."""
    if selected is None:
        return EDITORS
    unknown = sorted(set(selected) - set(EDITORS))
    if unknown:
        raise KeyError(f"Unknown editor(s): {', '.join(unknown)}")
    return {
        editor_key: EDITORS[editor_key]
        for editor_key in selected
    }

##
## === PROGRAM MAIN
##


def remove_symlinks(
    *,
    dry_run: bool,
    selected: tuple[str, ...] | None = None,
):
    _log_message("Started removing editor config symlinks")
    selected_editors = get_selected_editors(selected=selected)
    for editor in selected_editors.values():
        for file_name in editor.files:
            shell_actions.remove_symlink(
                target_path=editor.target_dir / f"{file_name}.json",
                script_name=SCRIPT_NAME,
                dry_run=dry_run,
            )
    _log_message("Finished removing editor config symlinks")


def run(
    *,
    dry_run: bool,
    selected: tuple[str, ...] | None = None,
):
    selected_editors = get_selected_editors(selected=selected)
    for editor in selected_editors.values():
        setup_editor(
            editor=editor,
            dry_run=dry_run,
        )
    _log_message("Finished setting up editors.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate and symlink editor settings.",
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
    args = parser.parse_args()
    profile = profiles.load_profile(profile_name=args.profile)
    run(
        dry_run=args.dry_run,
        selected=profile.editors if profile is not None else None,
    )

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
