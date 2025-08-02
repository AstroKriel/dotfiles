#!/usr/bin/env bash

## exit if any unset variable is used
set -u

## check for dry-run mode
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true
if $DRY_RUN; then
  echo -e "\033[1;34m[~]\033[0m Running in DRY-RUN mode: no changes will be made\n"
fi

## resolve absolute path to this script’s directory (your dotfiles repo root)
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

## logging functions
log()  { echo -e "\033[1;32m[+]\033[0m $*"; }
warn() { echo -e "\033[1;33m[!]\033[0m $*"; }

## check if using a compatible Bash version
if [[ "${BASH_VERSINFO[0]}" -lt 4 ]]; then
  warn "You're using an outdated Bash version ($BASH_VERSION)."
  warn "This script requires Bash 4.0 or newer."
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
  ["$DOTFILES_DIR/ghostty/config"]="$HOME/.config/ghostty/config"
  ## vscode
  ["$DOTFILES_DIR/vscode/settings.json"]="$HOME/Library/Application Support/Code/User/settings.json"
  ["$DOTFILES_DIR/vscode/keybindings.json"]="$HOME/Library/Application Support/Code/User/keybindings.json"
)

## create parent directories for target paths if they don't exist
create_parent_dir() {
  local target="$1"
  local parent
  parent="$(dirname "$target")"
  [[ -d "$parent" ]] || mkdir -p "$parent"
}

## backup existing non-symlink files by renaming
backup_existing() {
  local path="$1"
  local backup="${path}.pre-dotfiles"

  if [[ -e "$backup" ]]; then
    warn "Removing existing backup: $backup"
    $DRY_RUN || rm -rf "$backup"
  fi

  if $DRY_RUN; then
    log "[dry-run] Would rename $path -> $backup"
  else
    mv "$path" "$backup" && log "Renamed $path -> $backup"
  fi
}

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

  create_parent_dir "$target_path"

  ## skip if already correctly linked
  if [[ -L "$target_path" && "$(readlink "$target_path")" == "$source_path" ]]; then
    log "Already correctly linked: $target_path"
    continue
  fi

  ## if existing file/dir, back it up
  if [[ -e "$target_path" && ! -L "$target_path" ]]; then
    warn "Backing up existing file: $target_path"
    backup_existing "$target_path" || {
      warn "Failed to back up $target_path"
      ((fail_count++))
      failed_paths+=("$target_path")
      continue
    }

  ## if existing symlink, remove it
  elif [[ -L "$target_path" ]]; then
    if $DRY_RUN; then
      log "[dry-run] Would remove existing symlink: $target_path"
    else
      rm -f "$target_path" || {
        warn "Failed to remove symlink: $target_path"
        ((fail_count++))
        failed_paths+=("$target_path")
        continue
      }
    fi
  fi

  ## ensure source exists
  if [[ ! -e "$source_path" ]]; then
    warn "Source does not exist: $source_path"
    ((fail_count++))
    failed_paths+=("$target_path")
    continue
  fi

  ## create the symlink
  if $DRY_RUN; then
    log "[dry-run] Would link $source_path -> $target_path"
    ((success_count++))
  else
    log "Linking $source_path -> $target_path"
    if ln -s "$source_path" "$target_path"; then
      ((success_count++))
    else
      warn "Failed to link $source_path -> $target_path"
      ((fail_count++))
      failed_paths+=("$target_path")
    fi
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
  if $DRY_RUN; then
    log "[dry-run] Would install TPM in $TPM_DIR"
  else
    log "Installing TPM (Tmux Plugin Manager)..."
    git clone https://github.com/tmux-plugins/tpm "$TPM_DIR" || {
      warn "Failed to install TPM"
      ((fail_count++))
      failed_paths+=("$TPM_DIR")
    }
  fi
else
  log "TPM is already installed under $TPM_DIR"
fi

log "Finished setting up dotfiles."

## .