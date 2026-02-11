# robot3_seeds/seed_utils.py

def get_seed_command(action: str) -> str:
    """
    Convert UI action into seed dispenser command strings.
    """

    mapping = {
        "seed_power_on": "power_on",
        "seed_mode_auto": "auto",
        "seed_mode_manual": "manual",
        "seed_dispense_once": "dispense_once"
    }

    return mapping.get(action, "none")