# robot3_movements/movement_utils.py

def get_command(action: str) -> str:
    """
    Convert UI button action (up/down/left/right/stop)
    into the ESP32 command strings.
    """

    mapping = {
        "up": "forward",
        "down": "backward",
        "left": "left",
        "right": "right",
        "stop": "stop"
    }

    # return the mapped command or default to stop
    return mapping.get(action, "stop")
