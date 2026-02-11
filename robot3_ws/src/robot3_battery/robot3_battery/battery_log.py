import datetime
import os

LOG_FILE = os.path.expanduser("~/battery_log.txt")

def write_log(text):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.datetime.now()}] {text}\n")
    except Exception as e:
        print(f"Error writing battery log: {e}")
