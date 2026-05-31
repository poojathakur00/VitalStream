import logging
from typing import Optional

logger = logging.getLogger(__name__)


def score_resp_rate(value: Optional[float]) -> int:
    if value is None:
        return 0
    if value <= 8:
        return 3
    if value <= 11:
        return 1
    if value <= 20:
        return 0
    if value <= 24:
        return 2
    return 3


def score_spo2(value: Optional[float]) -> int:
    if value is None:
        return 0
    if value <= 91:
        return 3
    if value <= 93:
        return 2
    if value <= 95:
        return 1
    return 0


def score_bp_sys(value: Optional[float]) -> int:
    if value is None:
        return 0
    if value <= 90:
        return 3
    if value <= 100:
        return 2
    if value <= 110:
        return 1
    if value <= 219:
        return 0
    return 3


def score_heart_rate(value: Optional[float]) -> int:
    if value is None:
        return 0
    if value <= 40:
        return 3
    if value <= 50:
        return 1
    if value <= 90:
        return 0
    if value <= 110:
        return 1
    if value <= 130:
        return 2
    return 3


def score_temperature(value: Optional[float]) -> int:
    if value is None:
        return 0
    if value <= 35.0:
        return 3
    if value <= 36.0:
        return 1
    if value <= 38.0:
        return 0
    if value <= 39.0:
        return 1
    return 2


def get_risk_level(score: int) -> str:
    if score >= 12:
        return "CRITICAL"
    if score >= 7:
        return "HIGH"
    if score >= 5:
        return "MEDIUM"
    return "LOW"


def calculate_ews(row) -> dict:
    """
    Takes a pivoted row (one patient, one window) and returns EWS score.
    Row must have: heart_rate, spo2, blood_pressure_sys, temperature, resp_rate
    """
    hr_score   = score_heart_rate(row.heart_rate)
    spo2_score = score_spo2(row.spo2)
    bp_score   = score_bp_sys(row.blood_pressure_sys)
    temp_score = score_temperature(row.temperature)
    resp_score = score_resp_rate(row.resp_rate)

    total = hr_score + spo2_score + bp_score + temp_score + resp_score
    risk  = get_risk_level(total)

    logger.info(
        f"Patient {row.patient_id}: "
        f"HR={row.heart_rate:.1f}({hr_score}) "
        f"SpO2={row.spo2:.1f}({spo2_score}) "
        f"BP={row.blood_pressure_sys:.1f}({bp_score}) "
        f"Temp={row.temperature:.1f}({temp_score}) "
        f"Resp={row.resp_rate:.1f}({resp_score}) "
        f"→ Total={total} [{risk}]"
    )

    return {
        "score": total,
        "risk_level": risk,
        "hr_score": hr_score,
        "spo2_score": spo2_score,
        "bp_score": bp_score,
        "temp_score": temp_score,
        "resp_score": resp_score,
    }