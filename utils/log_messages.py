## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import datetime
from pathlib import Path
from typing import Callable

##
## === MODULE CONFIG
##

LOG_FILE = Path.home() / "dotfiles_log.txt"
_write_to_file = True

##
## === LOG FUNCTIONS
##


def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_message(
    *,
    script_name: str,
    message: str,
    log_file: Path = LOG_FILE,
) -> None:
    ## get time
    timestamp = get_timestamp()
    log_entry = f"[{timestamp}] ({script_name}): {message}\n"
    print(log_entry)
    if not _write_to_file:
        return
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(log_entry)


def configure(
    *,
    write_to_file: bool,
) -> None:
    global _write_to_file
    _write_to_file = write_to_file


def format_dry_run(
    *,
    message: str,
    dry_run: bool,
) -> str:
    if dry_run:
        return f"[dry-run] {message}"
    return message


def make_logger(
    script_name: str,
) -> Callable[[str], None]:
    def _log(
        message: str,
    ) -> None:
        log_message(
            script_name=script_name,
            message=message,
        )
    return _log

## } MODULE
