from processor.src.ews_scorer import calculate_ews, get_risk_level

class MockRow:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_normal_patient_is_low_risk():
    row = MockRow(
        patient_id="P001",
        heart_rate=75.0,
        spo2=97.0,
        blood_pressure_sys=120.0,
        temperature=37.0,
        resp_rate=16.0,
    )
    result = calculate_ews(row)
    assert result["score"] == 0
    assert result["risk_level"] == "LOW"

def test_critical_patient():
    row = MockRow(
        patient_id="P002",
        heart_rate=135.0,   # score 3
        spo2=90.0,          # score 3
        blood_pressure_sys=85.0,  # score 3
        temperature=39.5,   # score 2
        resp_rate=26.0,     # score 3
    )
    result = calculate_ews(row)
    assert result["score"] == 14
    assert result["risk_level"] == "CRITICAL"

def test_risk_levels():
    assert get_risk_level(0)  == "LOW"
    assert get_risk_level(4)  == "LOW"
    assert get_risk_level(5)  == "MEDIUM"
    assert get_risk_level(6)  == "MEDIUM"
    assert get_risk_level(7)  == "HIGH"
    assert get_risk_level(11) == "HIGH"
    assert get_risk_level(12) == "CRITICAL"