#!/usr/bin/env bash

## exit if any unset variable is used
set -u

## resolve absolute path to this script’s directory (your dotfiles repo root)
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

## create a timestamped backup directory in case any files need to be moved
BACKUP_DIR="$HOME/.dotfiles_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

## logging functions
log()  { echo -e "\033[1;32m[+]\033[0m $*"; }
warn() { echo -e "\033[1;33m[!]\033[0m $*"; }

## check if using a compatible Bash version
if [[ "${BASH_VERSINFO[0]}" -lt 4 ]]; then
  warn "You're using an outdated Bash version ($BASH_VERSION)."
  warn "This script requires Bash 4.0 or newer."
  warn "Please re-run using a newer Bash interpreter if you encounter issues."
  exit 1
fi

## define source-target symlinks
declare -A FILES=(
  ## bash
  ["$DOTFILES_DIR/bash/bashrc"]="$HOME/.bashrc"
  ["$DOTFILES_DIR/bash/bash_aliases"]="$HOME/.bash_aliases"
  ["$DOTFILES_DIR/bash/inputrc"]="$HOME/.inputrc"
  ## neovim
  ["$DOTFILES_DIR/nvim"]="$HOME/.config/nvim"
  ## tmux
  ["$DOTFILES_DIR/tmux/tmux.conf"]="$HOME/.config/tmux/tmux.conf"
  ["$DOTFILES_DIR/tmux/bin"]="$HOME/.config/tmux/bin"
  ## ghostty
  # ["$DOTFILES_DIR/ghostty/config"]="$HOME/Library/Application Support/com.mitchellh.ghostty/config"
  ["$DOTFILES_DIR/ghostty/config"]="$HOME/.config/ghostty/config"
)

## create parent directories for target paths if they don't exist
create_parent_dir() {
  local target="$1"
  local parent
  parent="$(dirname "$target")"
  [[ -d "$parent" ]] || mkdir -p "$parent"
}

## counters for summary reporting
success_count=0
fail_count=0
failed_paths=()

## get sorted list of keys to ensure deterministic ordering
mapfile -t sorted_keys < <(printf "%s\n" "${!FILES[@]}" | sort)

## print planned links
echo "Resolved dotfile links:"
for source_path in "${sorted_keys[@]}"; do
  target_path="${FILES[$source_path]}"
  echo "> $source_path -> $target_path"
done
echo ""

## main symlinking loop
echo "Attempting symlink"
for source_path in "${sorted_keys[@]}"; do
  target_path="${FILES[$source_path]}"
  log "Processing $source_path -> $target_path"

  ## ensure target directory exists
  create_parent_dir "$target_path"

  ## if a non-symlink file already exists, back it up
  if [[ -e "$target_path" && ! -L "$target_path" ]]; then
    warn "Backing up existing file: $target_path -> $BACKUP_DIR"
    mv "$target_path" "$BACKUP_DIR/" || {
      warn "Failed to backup $target_path"
      ((fail_count++))
      failed_paths+=("$target_path")
      continue
    }

  ## if target is a symlink, remove it
  elif [[ -L "$target_path" ]]; then
    rm -f "$target_path" || {
      warn "Failed to remove existing symlink $target_path"
      ((fail_count++))
      failed_paths+=("$target_path")
      continue
    }
  fi

  ## ensure the source file actually exists
  if [[ ! -e "$source_path" ]]; then
    warn "Source file does not exist: $source_path"
    ((fail_count++))
    failed_paths+=("$target_path")
    continue
  fi

  ## attempt to create the symlink
  log "Linking $source_path -> $target_path"
  if ln -s "$source_path" "$target_path"; then
    ((success_count++))
  else
    warn "Failed to link $source_path -> $target_path"
    ((fail_count++))
    failed_paths+=("$target_path")
  fi
done

## print summary report
echo ""
if (( fail_count == 0 )); then
  log "Successfully linked all dotfiles!"
else
  warn "$fail_count dotfiles failed to link:"
  for failed_path in "${failed_paths[@]}"; do
    warn "  - $failed_path"
  done
  exit 1
fi

## install TPM if not already installed
TPM_DIR="$HOME/.config/tmux/plugins/tpm"
if [[ ! -d "$TPM_DIR" ]]; then
  log "Installing TPM (Tmux Plugin Manager)..."
  git clone https://github.com/tmux-plugins/tpm "$TPM_DIR" || {
    warn "Failed to install TPM"
    ((fail_count++))
    failed_paths+=("$TPM_DIR")
  }
else
  log "TPM is already installed under $TPM_DIR"
fi


log "Finished setting up dotfiles."

## .