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
    log_file.parent.mkdir(parents=True, exist_ok=True)
    print(log_entry)
    with open(log_file, "a") as f:
        f.write(log_entry)


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
