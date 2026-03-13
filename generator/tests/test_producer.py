"""Tests for the vital signs generator."""

import json
from datetime import datetime

from generator.src.config import VITAL_TOPICS
from generator.src.patient_profiles import generate_patient_profiles
from generator.src.producer import generate_reading


# ---- Patient profile tests ----

def test_generates_correct_number_of_patients():
    profiles = generate_patient_profiles(20)
    assert len(profiles) == 20


def test_patient_ids_are_unique():
    profiles = generate_patient_profiles(20)
    ids = [p["patient_id"] for p in profiles]
    assert len(ids) == len(set(ids))


def test_patient_id_format():
    profiles = generate_patient_profiles(5)
    for profile in profiles:
        assert profile["patient_id"].startswith("P")
        assert len(profile["patient_id"]) == 4  # P001


def test_patient_has_required_fields():
    profiles = generate_patient_profiles(1)
    patient = profiles[0]
    required = ["patient_id", "name", "age", "gender", "ward", "baselines"]
    for field in required:
        assert field in patient, f"Missing field: {field}"


def test_patient_age_is_realistic():
    profiles = generate_patient_profiles(20)
    for patient in profiles:
        assert 25 <= patient["age"] <= 85


# ---- Vital sign reading tests ----

def test_reading_has_correct_format():
    profiles = generate_patient_profiles(1)
    reading = generate_reading(profiles[0], "heart_rate")
    required = ["patient_id", "vital_type", "value", "unit", "timestamp"]
    for field in required:
        assert field in reading, f"Missing field: {field}"


def test_reading_value_is_number():
    profiles = generate_patient_profiles(1)
    reading = generate_reading(profiles[0], "heart_rate")
    assert isinstance(reading["value"], float)


def test_reading_timestamp_is_valid_iso():
    profiles = generate_patient_profiles(1)
    reading = generate_reading(profiles[0], "heart_rate")
    # This will raise if the timestamp is not valid ISO format
    datetime.fromisoformat(reading["timestamp"])


def test_reading_is_json_serializable():
    profiles = generate_patient_profiles(1)
    reading = generate_reading(profiles[0], "heart_rate")
    serialized = json.dumps(reading)
    assert isinstance(serialized, str)


# ---- Physiological range tests ----

def test_heart_rate_within_range():
    profiles = generate_patient_profiles(1)
    for _ in range(100):
        reading = generate_reading(profiles[0], "heart_rate")
        assert 30 <= reading["value"] <= 200


def test_spo2_within_range():
    profiles = generate_patient_profiles(1)
    for _ in range(100):
        reading = generate_reading(profiles[0], "spo2")
        assert 70 <= reading["value"] <= 100


def test_temperature_within_range():
    profiles = generate_patient_profiles(1)
    for _ in range(100):
        reading = generate_reading(profiles[0], "temperature")
        assert 34.0 <= reading["value"] <= 42.0


def test_blood_pressure_sys_within_range():
    profiles = generate_patient_profiles(1)
    for _ in range(100):
        reading = generate_reading(profiles[0], "blood_pressure_sys")
        assert 60 <= reading["value"] <= 250


def test_resp_rate_within_range():
    profiles = generate_patient_profiles(1)
    for _ in range(100):
        reading = generate_reading(profiles[0], "resp_rate")
        assert 5 <= reading["value"] <= 45


# ---- Topic mapping tests ----

def test_all_vital_types_have_topics():
    expected_vitals = [
        "heart_rate", "blood_pressure_sys", "blood_pressure_dia",
        "spo2", "temperature", "resp_rate",
    ]
    for vital in expected_vitals:
        assert vital in VITAL_TOPICS


def test_all_vital_types_generate_readings():
    profiles = generate_patient_profiles(1)
    for vital_type in VITAL_TOPICS:
        reading = generate_reading(profiles[0], vital_type)
        assert reading["vital_type"] == vital_type