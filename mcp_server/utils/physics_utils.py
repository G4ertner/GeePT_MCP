from __future__ import annotations

import math

G0 = 9.80665  # m/s^2


def simple_burn_time(mass_kg: float, thrust_n: float, dv_m_s: float) -> float | None:
    if not mass_kg or not thrust_n or not dv_m_s:
        return None
    if mass_kg <= 0 or thrust_n <= 0 or dv_m_s <= 0:
        return None
    return dv_m_s * mass_kg / thrust_n


def tsiolkovsky_burn_time(mass_kg: float, thrust_n: float, isp_s: float | None, dv_m_s: float) -> float | None:
    if not isp_s or isp_s <= 0:
        return None
    simple = simple_burn_time(mass_kg, thrust_n, dv_m_s)
    if simple is None:
        return None
    try:
        return (isp_s * G0 * (1.0 - math.exp(-dv_m_s / (G0 * isp_s))) * mass_kg) / thrust_n
    except OverflowError:
        return None
