## { SCRIPT

##
## === DEPENDENCIES
##

## stdlib
import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil
import sys

## local
from utils import load_profiles
from utils import log_messages, apply_shell_actions

##
## === TOOL CONFIG
##

HOME_DIR = Path.home()
SCRIPT_NAME = Path(__file__).name
ROOT_DIR = Path(__file__).resolve().parent.parent
DOTFILES_DIR = ROOT_DIR / "tools"
CONFIG_DIR = HOME_DIR / ".config"

_log_message = log_messages.make_logger(SCRIPT_NAME)


@dataclass
class RepoConfig:
    name: str
    url: str
    output: Path


@dataclass
class ToolConfig:
    name: str
    brew: str
    dotfiles_dir: Path
    target_dir: Path
    mac_app: str | None = None
    clone_repo: RepoConfig | None = None


TOOLS: dict[str, ToolConfig] = {
    "tmux": ToolConfig(
        name="Tmux",
        brew="tmux",
        dotfiles_dir=DOTFILES_DIR / "tmux",
        target_dir=CONFIG_DIR / "tmux",
        clone_repo=RepoConfig(
            name="TPM",
            url="https://github.com/tmux-plugins/tpm",
            output=CONFIG_DIR / "tmux" / "plugins" / "tpm",
        ),
    ),
    "kitty": ToolConfig(
        name="Kitty terminal",
        brew="kitty --cask",
        mac_app="kitty.app",
        dotfiles_dir=DOTFILES_DIR / "kitty",
        target_dir=CONFIG_DIR / "kitty",
    ),
    "ghostty": ToolConfig(
        name="Ghostty terminal",
        brew="ghostty --cask",
        mac_app="Ghostty.app",
        dotfiles_dir=DOTFILES_DIR / "ghostty",
        target_dir=CONFIG_DIR / "ghostty",
    ),
    "yazi": ToolConfig(
        name="Yazi",
        brew="yazi ffmpeg",
        dotfiles_dir=DOTFILES_DIR / "yazi",
        target_dir=CONFIG_DIR / "yazi",
    ),
}

##
## === TOOL HELPERS
##


def get_selected_tools(
    *,
    selected: tuple[str, ...] | None,
) -> dict[str, ToolConfig]:
    """Return tool configs selected by the active system profile."""
    if selected is None:
        return TOOLS
    unknown = sorted(set(selected) - set(TOOLS))
    if unknown:
        raise KeyError(f"Unknown tool(s): {', '.join(unknown)}")
    return {
        tool_key: TOOLS[tool_key]
        for tool_key in selected
    }


def resolve_selected_tools(
    *,
    profile_selected: tuple[str, ...] | None,
    requested: tuple[str, ...],
    include_all: bool,
) -> tuple[str, ...] | None:
    if include_all:
        return None
    if not requested:
        return profile_selected
    get_selected_tools(selected=requested)
    if profile_selected is None:
        return requested
    unavailable = sorted(set(requested) - set(profile_selected))
    if unavailable:
        raise KeyError(
            "Requested tool(s) are not subscribed by the active profile: "
            f"{', '.join(unavailable)}",
        )
    return requested


def check_installed_tools(
    *,
    selected: tuple[str, ...] | None,
):
    """Return subscribed tools that are installed on this system."""
    _log_message("Checking installed tools...")
    available = set()
    selected_tools = get_selected_tools(selected=selected)
    for command, tool in selected_tools.items():
        found_via_app = (
            sys.platform == "darwin"
            and tool.mac_app is not None
            and (Path("/Applications") / tool.mac_app).exists()
        )
        if shutil.which(command) or found_via_app:
            _log_message(f"Found {tool.name} ({command}) in your `$PATH`.")
            available.add(command)
        else:
            _log_message(
                f"{tool.name} was not found in your `$PATH`.\n"
                f"Install it via: `brew install {tool.brew}`",
            )
    return available


def shallow_clone_repo(
    *,
    repo: RepoConfig,
    dry_run: bool,
):
    if repo.output.exists():
        _log_message(f"{repo.name} already exists under: {repo.output}")
        return
    apply_shell_actions.run_command(
        args=["git", "clone", "--depth", "1", repo.url, str(repo.output)],
        script_name=SCRIPT_NAME,
        description=f"clone {repo.name} (shallow) under {repo.output}",
        dry_run=dry_run,
    )


##
## === PROGRAM MAIN
##


def remove_symlinks(
    *,
    dry_run: bool,
    selected: tuple[str, ...] | None = None,
):
    log_messages.configure(write_to_file=not dry_run)
    _log_message("Started removing tool config symlinks")
    selected_tools = get_selected_tools(selected=selected)
    for tool in selected_tools.values():
        apply_shell_actions.remove_symlink(
            target_path=tool.target_dir,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    _log_message("Finished removing tool config symlinks")


def run(
    *,
    dry_run: bool,
    check_only: bool = False,
    selected: tuple[str, ...] | None = None,
):
    log_messages.configure(write_to_file=not dry_run)
    ## log start of script
    _log_message("Started setting up tool configs")
    available_tools = check_installed_tools(selected=selected)
    if check_only:
        _log_message("Check complete. Exiting due to `--check-only`")
        return
    ## symlink each config directory to ~/.config/
    for command in sorted(available_tools):
        tool = TOOLS[command]
        apply_shell_actions.ensure_dir_exists(
            directory=tool.target_dir.parent,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
        apply_shell_actions.create_symlink(
            source_path=tool.dotfiles_dir,
            target_path=tool.target_dir,
            script_name=SCRIPT_NAME,
            dry_run=dry_run,
        )
    ## git clone repos
    for command in available_tools:
        tool = TOOLS[command]
        if tool.clone_repo is not None:
            shallow_clone_repo(
                repo=tool.clone_repo,
                dry_run=dry_run,
            )
    ## log end of script
    _log_message("Finished setting up tool configs")


def main():
    ## parse user inputs
    parser = argparse.ArgumentParser(
        description="Symlink subscribed tool config folders and clone needed repos.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without applying them",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check installed tools and exit",
    )
    parser.add_argument(
        "--profile",
        help="Load selected tools from profiles/<name>.toml",
    )
    parser.add_argument(
        "--tool",
        action="append",
        choices=sorted(TOOLS),
        default=[],
        help="Apply one subscribed tool. Can be passed multiple times",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Apply all known tools, ignoring profile tool subscriptions",
    )
    args = parser.parse_args()
    if args.all and args.tool:
        parser.error("--all cannot be combined with --tool")
    profile = load_profiles.load_profile(profile_name=args.profile)
    selected = resolve_selected_tools(
        profile_selected=profile.tools if profile is not None else None,
        requested=tuple(args.tool),
        include_all=args.all,
    )
    run(
        dry_run=args.dry_run,
        check_only=args.check_only,
        selected=selected,
    )

##
## === ENTRY POINT
##

if __name__ == "__main__":
    main()

## } SCRIPT
