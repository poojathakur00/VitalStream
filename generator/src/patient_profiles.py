"""Synthetic patient definitions with baseline vital sign ranges."""

import random
from typing import Any


def generate_patient_profiles(num_patients: int) -> list[dict[str, Any]]:
    """Generate synthetic patient profiles with realistic baseline vitals.

    Each patient gets a baseline range for every vital sign. The generator
    will later produce readings that fluctuate around these baselines.

    Args:
        num_patients: How many patients to create.

    Returns:
        List of patient dictionaries with demographics and vital baselines.
    """
    first_names = [
        "James", "Mary", "Robert", "Linda", "Michael",
        "Sarah", "David", "Karen", "Richard", "Susan",
        "Thomas", "Nancy", "Joseph", "Lisa", "Charles",
        "Betty", "Daniel", "Dorothy", "Matthew", "Helen",
    ]

    wards = ["ICU", "Cardiology", "General", "Neurology", "Respiratory"]

    profiles = []

    for i in range(num_patients):
        patient_id = f"P{i + 1:03d}"  # P001, P002, ..., P020
        age = random.randint(25, 85)

        # Older patients tend to have slightly different baselines
        age_factor = age / 60  # >1 for older, <1 for younger

        profile = {
            "patient_id": patient_id,
            "name": first_names[i % len(first_names)],
            "age": age,
            "gender": random.choice(["Male", "Female"]),
            "ward": random.choice(wards),
            "baselines": {
                "heart_rate": {
                    "mean": 70 + (age_factor * 10),
                    "std": 5.0,
                    "unit": "bpm",
                },
                "blood_pressure_sys": {
                    "mean": 110 + (age_factor * 15),
                    "std": 8.0,
                    "unit": "mmHg",
                },
                "blood_pressure_dia": {
                    "mean": 70 + (age_factor * 8),
                    "std": 5.0,
                    "unit": "mmHg",
                },
                "spo2": {
                    "mean": 97 - (age_factor * 1.5),
                    "std": 1.0,
                    "unit": "%",
                },
                "temperature": {
                    "mean": 37.0,
                    "std": 0.3,
                    "unit": "°C",
                },
                "resp_rate": {
                    "mean": 14 + (age_factor * 2),
                    "std": 2.0,
                    "unit": "breaths/min",
                },
            },
        }

        profiles.append(profile)

    return profiles