import datetime
import os

# Separate sensor log file (avoid conflict with UI log file)
LOG_FILE = os.path.expanduser("~/robot3_sensor_log.txt")


def write_log_once(text: str):
    """
    Writes a log entry only if the same text was not logged before.
    Prevents duplicate spam.
    """
    timestamped = f"[{datetime.datetime.now()}] {text}"

    # Ensure file exists
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()

    # Check if this entry already exists
    with open(LOG_FILE, "r") as f:
        if text in f.read():
            return

    # Write new entry
    with open(LOG_FILE, "a") as f:
        f.write(timestamped + "\n")
