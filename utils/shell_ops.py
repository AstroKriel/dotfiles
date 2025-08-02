from pathlib import Path
from typing import Optional
from utils.logging import get_timestamp, log_message

def ensure_dir_exists(
    directory   : Path,
    script_name : str,
    dry_run     : bool = False
  ):
  """
  Ensure a directory exists, creating it if needed.
  """
  ## do nothing if already exists
  if directory.exists():
    return
  if dry_run:
    log_message(script_name=script_name, message=f"[dry-run] Would create directory: {directory}")
  else:
    log_message(script_name=script_name, message=f"Creating directory: {directory}")
    directory.mkdir(parents=True, exist_ok=True)

def backup_file(
    target_path : Path,
    script_name : str,
    dry_run     : bool = False
  ) -> Optional[Path]:
  """
  Backup a file or symlink:
  - if symlink: remove and log resolved target
  - if real file: rename with timestamp
  Returns the backup path if renamed, or None otherwise.
  """
  ## skip if nothing exists at the path
  if not target_path.exists() and not target_path.is_symlink():
    return None
  ## handle symbolic links separately
  if target_path.is_symlink():
    try:
      ## attempt to resolve what the symlink points to (may fail if broken)
      resolved = target_path.resolve()
      log_message(script_name=script_name, message=f"{target_path} (symlink) -> {resolved}")
    except Exception as e:
      ## broken or unresolvable symlink
      log_message(script_name=script_name, message=f"Warning: failed to resolve symlink {target_path}: {e}")
    if dry_run:
      log_message(script_name=script_name, message=f"[dry-run] Would remove symlink: {target_path}")
    else:
      target_path.unlink()
      log_message(script_name=script_name, message=f"Removed symlink: {target_path}")
    return None
  ## for real files/dirs, rename in place
  backup_path = _rename_with_timestamp(target_path, script_name, dry_run=dry_run)
  if backup_path:
    log_message(script_name=script_name, message=f"{target_path} -> {backup_path}")
  return backup_path

def _rename_with_timestamp(
    target_path  : Path,
    script_name  : str,
    dry_run      : bool = False
  ) -> Optional[Path]:
  """
  Rename a file or directory in place by appending a timestamp.
  Returns the backup path, or None if no rename was needed.
  """
  ## skip if nothing exists at the path (incl. broken symlinks)
  if not target_path.exists() and not target_path.is_symlink():
    return None
  ## generate a timestamped backup name
  timestamp = get_timestamp()
  backup_path = target_path.with_name(f"{target_path.name}.{timestamp}")
  if dry_run:
    log_message(script_name=script_name, message=f"[dry-run] Would rename {target_path} -> {backup_path}")
  else:
    log_message(script_name=script_name, message=f"Renaming {target_path} -> {backup_path}")
    target_path.rename(backup_path)
  return backup_path

def create_symlink(
    source_path : Path,
    target_path : Path,
    script_name : str,
    dry_run     : bool = False
  ):
  """
  Create a symlink from target_path to source_path, handling backup and safety checks.
  """
  ## case 1: target does not exist
  if not target_path.exists() and not target_path.is_symlink():
    _make_symlink(source_path, target_path, script_name, dry_run)
    return
  ## case 2: target is already correctly linked to source
  if _already_linked_correctly(target_path, source_path):
    log_message(script_name=script_name, message=f"Already correctly linked: {target_path}")
    return
  ## case 3: target points to something else. check types match before replacing
  if not _types_match(source_path, target_path):
    log_message(script_name=script_name, message=f"Type mismatch: {target_path} is {'dir' if target_path.is_dir() else 'file'}, "
                             f"but source is {'dir' if source_path.is_dir() else 'file'}. Skipping.")
    return
  ## back up and replace
  backup_file(target_path, script_name, dry_run=dry_run)
  _make_symlink(source_path, target_path, script_name, dry_run)

def _make_symlink(
    source_path : Path,
    target_path : Path,
    script_name : str,
    dry_run     : bool
  ):
  """
  Create a symlink with logging.
  """
  if dry_run:
    log_message(script_name=script_name, message=f"[dry-run] Would symlink: {source_path} -> {target_path}")
  else:
    log_message(script_name=script_name, message=f"Symlinking: {source_path} -> {target_path}")
    target_path.symlink_to(source_path)

def _already_linked_correctly(target_path: Path, source_path: Path) -> bool:
  """
  Returns true if target_path is a symlink to source_path.
  """
  try:
    return target_path.is_symlink() and (target_path.resolve() == source_path.resolve())
  except Exception:
    return False

def _types_match(source_path: Path, target_path: Path) -> bool:
  """
  Returns true if both are the same type (either file or directory).
  """
  if source_path.is_file() and target_path.is_file():
    return True
  if source_path.is_dir() and target_path.is_dir():
    return True
  return False

## .