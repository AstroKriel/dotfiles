import datetime
from pathlib import Path

LOG_FILE = Path.home() / "dotfiles_log.txt"

def get_timestamp():
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_message(
    *,
    script_name : str,
    message     : str,
    log_file    : Path = LOG_FILE
  ):
  ## get time
  timestamp = get_timestamp()
  log_entry = f"[{timestamp}] ({script_name}): {message}\n"
  log_file.parent.mkdir(parents=True, exist_ok=True)
  print(log_entry)
  with open(log_file, "a") as f:
    f.write(log_entry)

## .