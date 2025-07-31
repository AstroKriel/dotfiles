#!/usr/bin/env bash
set -euo pipefail

## ---------------------
## SETTINGS
## ---------------------

## default dotfiles location, with override support
DOTFILES_DIR="${DOTFILES_DIR:-$HOME/dotfiles}"
SHELL_DIR="$DOTFILES_DIR/shell"
BACKUP_DIR="$HOME/.dotfiles_backup"
DRY_RUN=0

## ---------------------
## ARGUMENT PARSING
## ---------------------

## expect a shell name and optional --dry-run flag
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 [bash|zsh] [--dry-run]"
  exit 1
fi

shell_choice="$1"
shift

if [[ $# -eq 1 && "$1" == "--dry-run" ]]; then
  DRY_RUN=1
fi

## ---------------------
## HELPERS
## ---------------------

## backup existing file and replace with symlink to source_path
backup_and_link() {
  local source_path="$1"
  local target_path="$2"
  local timestamp
  timestamp=$(date +%Y%m%d-%H%M%S)
  local base_name
  base_name=$(basename "$target_path")
  local backup_path="$BACKUP_DIR/${base_name}.${timestamp}"

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    echo "Backing up $target_path to $backup_path"
    [[ "$DRY_RUN" -eq 0 ]] && mkdir -p "$BACKUP_DIR" && mv "$target_path" "$backup_path"
  fi

  echo "Linking $target_path to $source_path"
  [[ "$DRY_RUN" -eq 0 ]] && ln -s "$source_path" "$target_path"
}

## remove files from the shell not being installed, with backup
remove_other_shell_configs() {
  local shell="$1"
  local timestamp
  timestamp=$(date +%Y%m%d-%H%M%S)

  local shared_files=(.shell_options .shell_aliases .shell_functions .shell_paths)

  if [[ "$shell" == "zsh" ]]; then
    local shell_files=(.bashrc .bash_options .bash_prompt .inputrc)
  elif [[ "$shell" == "bash" ]]; then
    local shell_files=(.zshrc .zsh_options .zsh_prompt)
  else
    echo "Unsupported shell: $shell"
    exit 1
  fi

  for f in "${shell_files[@]}" "${shared_files[@]}"; do
    [[ -e "$HOME/$f" || -L "$HOME/$f" ]] || continue
    echo "Backing up and removing $HOME/$f"
    [[ "$DRY_RUN" -eq 0 ]] && mkdir -p "$BACKUP_DIR" && mv "$HOME/$f" "$BACKUP_DIR/${f}.${timestamp}"
  done
}

## link bash-related dotfiles from repo into home directory
link_bash() {
  echo "Linking Bash dotfiles..."
  backup_and_link "$SHELL_DIR/bash/bashrc"        "$HOME/.bashrc"
  backup_and_link "$SHELL_DIR/bash/bash_options"  "$HOME/.bash_options"
  backup_and_link "$SHELL_DIR/bash/bash_prompt"   "$HOME/.bash_prompt"
  backup_and_link "$SHELL_DIR/bash/inputrc"       "$HOME/.inputrc"
}

## link zsh-related dotfiles from repo into home directory
link_zsh() {
  echo "Linking Zsh dotfiles..."
  backup_and_link "$SHELL_DIR/zsh/zshrc"       "$HOME/.zshrc"
  backup_and_link "$SHELL_DIR/zsh/zsh_options" "$HOME/.zsh_options"
  backup_and_link "$SHELL_DIR/zsh/zsh_prompt"  "$HOME/.zsh_prompt"
}

## link shell-agnostic utility files (used by both shells)
link_shared_utils() {
  backup_and_link "$SHELL_DIR/utils/aliases"   "$HOME/.shell_aliases"
  backup_and_link "$SHELL_DIR/utils/functions" "$HOME/.shell_functions"
  backup_and_link "$SHELL_DIR/utils/env"       "$HOME/.shell_options"
  backup_and_link "$SHELL_DIR/utils/paths"     "$HOME/.shell_paths"
}

## change login shell if needed
change_login_shell() {
  local shell_name="$1"
  local shell_path
  shell_path="$(command -v "$shell_name")"

  if [[ -z "$shell_path" || ! -x "$shell_path" ]]; then
    echo "Shell executable for '$shell_name' not found or not executable"
    exit 1
  fi

  if [[ "$OSTYPE" == "darwin"* ]]; then
    current_shell="$(dscl . -read /Users/$USER UserShell | awk '{print $2}')"
  else
    current_shell="$(getent passwd "$USER" | cut -d: -f7)"
  fi

  if [[ "$current_shell" != "$shell_path" ]]; then
    echo "Changing login shell to: $shell_path"
    chsh -s "$shell_path"
  else
    echo "Login shell is already set to $shell_path"
  fi
}

## ---------------------
## MAIN
## ---------------------

case "$shell_choice" in
  bash)
    remove_other_shell_configs bash
    link_bash
    link_shared_utils
    ;;
  zsh)
    remove_other_shell_configs zsh
    link_zsh
    link_shared_utils
    ;;
  *)
    echo "Unsupported shell: $shell_choice"
    echo "Usage: $0 [bash|zsh] [--dry-run]"
    exit 1
    ;;
esac

if [[ "$DRY_RUN" -eq 0 ]]; then
  change_login_shell "$shell_choice"
else
  echo "(Dry run: no changes were made)"
fi

echo "$shell_choice setup complete."

## .