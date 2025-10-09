from pathlib import Path
from typing import Optional
from utils.logging import get_timestamp, log_message


def ensure_dir_exists(
    *,
    directory: Path,
    script_name: str,
    dry_run: bool = False,
):
    """
  Ensure that the directory exists. Create it if it does not.
  """
    ## do nothing if already exists
    if directory.exists():
        return
    if dry_run:
        log_message(
            script_name=script_name,
            message=f"[dry-run] Would create directory: {directory}",
        )
    else:
        directory.mkdir(parents=True, exist_ok=True)
        log_message(
            script_name=script_name,
            message=f"Created directory: {directory}",
        )


def backup_file(
    *,
    target_path: Path,
    script_name: str,
    dry_run: bool = False,
) -> Optional[Path]:
    """
  Backup a file or symlink at the given path.

  If the target is a symlink, remove it. If it is a real file or directory, rename it with a timestamp.
  Return the backup path if a rename was performed, otherwise return None.
  """
    ## skip if nothing exists at the path
    if not target_path.exists() and not target_path.is_symlink():
        return None
    ## handle symbolic links separately
    if target_path.is_symlink():
        try:
            ## attempt to resolve what the symlink points to (may fail if broken)
            resolved = target_path.resolve()
            log_message(
                script_name=script_name,
                message=f"{target_path} (symlink) -> {resolved}",
            )
        except Exception as e:
            ## broken or unresolvable symlink
            log_message(
                script_name=script_name,
                message=f"Warning: failed to resolve symlink {target_path}: {e}",
            )
        if dry_run:
            log_message(
                script_name=script_name,
                message=f"[dry-run] Would remove symlink: {target_path}",
            )
        else:
            target_path.unlink()
            log_message(
                script_name=script_name,
                message=f"Removed symlink: {target_path}",
            )
        return None
    ## for real files/dirs, rename in place
    backup_path = _rename_with_timestamp(
        target_path=target_path,
        script_name=script_name,
        dry_run=dry_run,
    )
    if backup_path:
        log_message(
            script_name=script_name,
            message=f"{target_path} -> {backup_path}",
        )
    return backup_path


def _rename_with_timestamp(
    *,
    target_path: Path,
    script_name: str,
    dry_run: bool = False,
) -> Optional[Path]:
    """
  Rename a file or directory in place by appending a timestamp.

  Return the new backup path if the rename was performed, otherwise return None.
  """
    ## skip if nothing exists at the path (incl. broken symlinks)
    if not target_path.exists() and not target_path.is_symlink():
        return None
    ## generate a timestamped backup name
    timestamp = get_timestamp().replace(" ", ".")
    backup_path = target_path.with_stem(f"{target_path.stem}.{timestamp}")
    if dry_run:
        log_message(
            script_name=script_name,
            message=f"[dry-run] Would rename {target_path} -> {backup_path}",
        )
    else:
        log_message(
            script_name=script_name,
            message=f"Renaming {target_path} -> {backup_path}",
        )
        target_path.rename(backup_path)
    return backup_path


def create_symlink(
    *,
    source_path: Path,
    target_path: Path,
    script_name: str,
    dry_run: bool = False,
):
    """
  Create a symlink from target_path to source_path.

  Handle existing files by checking correctness, backing up if needed, and logging all actions.
  """
    ## source does not exist
    if not source_path.exists():
        log_message(
            script_name=script_name,
            message=f"Skipping. {source_path} does not exist.",
        )
        return
    ## target does not exist
    if _path_is_missing(target_path):
        _make_symlink(
            source_path=source_path,
            target_path=target_path,
            script_name=script_name,
            dry_run=dry_run,
        )
        return
    ## target is already correctly linked to source
    if _already_linked_correctly(target_path=target_path, source_path=source_path):
        log_message(
            script_name=script_name,
            message=f"Already correctly linked: {target_path}",
        )
        return
    ## target points to something else
    if _symlink_is_broken(target_path):
        log_message(
            script_name=script_name,
            message=f"Skipping. {target_path} is a broken symlink.",
        )
        return
    ## check types match before replacing
    if not _types_match(source_path=source_path, target_path=target_path):
        log_message(
            script_name=script_name,
            message=f"Skipping due to a type mismatch. {target_path} is {_get_path_type(target_path)}, "
            f"but source is {_get_path_type(source_path)}.",
        )
        return
    ## back up and replace
    backup_file(
        target_path=target_path,
        script_name=script_name,
        dry_run=dry_run,
    )
    _make_symlink(
        source_path=source_path,
        target_path=target_path,
        script_name=script_name,
        dry_run=dry_run,
    )


def _path_is_missing(path: Path) -> bool:
    """
  Return True if the path does not exist and is not a symlink.
  """
    return not path.exists() and not path.is_symlink()


def _symlink_is_broken(path: Path) -> bool:
    """
  Return True if the path is a symlink but its target does not exist.
  """
    return path.is_symlink() and not path.exists()


def _get_path_type(path: Path) -> str:
    """
  Return a description of the path type: file, dir, symlink, broken symlink, or unknown.
  """
    if path.is_dir():
        return "dir"
    elif path.is_file():
        return "file"
    elif path.is_symlink():
        return "broken symlink" if not path.exists() else "symlink"
    return "unknown"


def _make_symlink(
    *,
    source_path: Path,
    target_path: Path,
    script_name: str,
    dry_run: bool,
):
    """
  Create a symlink from target_path to source_path.
  """
    if dry_run:
        log_message(
            script_name=script_name,
            message=f"[dry-run] Would symlink: {source_path} -> {target_path}",
        )
    else:
        target_path.symlink_to(source_path)
        log_message(
            script_name=script_name,
            message=f"Symlinked: {source_path} -> {target_path}",
        )


def _already_linked_correctly(
    *,
    target_path: Path,
    source_path: Path,
) -> bool:
    """
  Check if the target is a symlink that points to the given source path.
  """
    try:
        return target_path.is_symlink() and (target_path.resolve() == source_path.resolve())
    except Exception:
        return False


def _types_match(
    *,
    source_path: Path,
    target_path: Path,
) -> bool:
    """
  Check whether both paths point to the same type.
  """
    if source_path.is_file() and target_path.is_file():
        return True
    if source_path.is_dir() and target_path.is_dir():
        return True
    return False


## .
