# robot3_battery/robot3_battery/battery_utils.py

from typing import List, Tuple

def voltage_to_percent(v: float, cells: int = 4) -> float:
    """
    Convert Li-ion pack voltage to % using interpolation table.
    """
    if v <= 0:
        return 0.0

    per_cell = v / float(cells)

    table: List[Tuple[float, float]] = [
        (4.20, 100.0),
        (3.90, 75.0),
        (3.70, 50.0),
        (3.50, 25.0),
        (3.20, 0.0),
    ]

    if per_cell >= table[0][0]:
        return 100.0
    if per_cell <= table[-1][0]:
        return 0.0

    for i in range(len(table) - 1):
        v_hi, p_hi = table[i]
        v_lo, p_lo = table[i+1]

        if v_hi >= per_cell >= v_lo:
            if v_hi == v_lo:
                return float(p_lo)
            t = (per_cell - v_lo) / (v_hi - v_lo)
            percent = p_lo + t * (p_hi - p_lo)
            return float(max(0.0, min(100.0, percent)))

    return 0.0
