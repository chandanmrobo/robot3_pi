def is_changed(previous: float, current: float, threshold: float = 0.5) -> bool:
    """
    True if new value differs enough to be considered a real change.
    Prevents UI/log spam.
    """
    if previous is None:
        return True

    return abs(current - previous) >= threshold
