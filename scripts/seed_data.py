"""Seed the VitalStream database with sample data."""

import sys
import logging

import psycopg2

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0,".")
from database.config import DB_CONFIG
from generator.src.patient_profiles import generate_patient_profiles
from generator.src.producer import generate_reading
from generator.src.config import VITAL_TOPICS

from datetime import datetime, timezone, timedelta
from typing import Any

logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def seed_patients(conn) -> None:
    """Insert 20 patinents into the patients table."""
    
    cursor= conn.cursor()
    profiles = generate_patient_profiles(20)


    for patient in profiles:
        pvital= seed_vitals(patient)

        cursor.execute("INSERT INTO patients (patient_id, name, age, gender, ward) VALUES (%s, %s, %s, %s, %s)",
        (patient["patient_id"], patient["name"], patient["age"], patient["gender"], patient["ward"]))

        for reading in pvital:
            cursor.execute("INSERT INTO vital_signs (patient_id, vital_type, value, unit, recorded_at) VALUES (%s, %s, %s, %s, %s)",
            (reading["patient_id"], reading["vital_type"], reading["value"], reading["unit"], reading["timestamp"]))

    conn.commit()
    cursor.close()

    logger.info(f"Inserted {len(profiles)} patients")


def seed_vitals(patient: dict[str, Any]) -> list[dict[str, Any]]:
    vital_type= VITAL_TOPICS.keys()

    readings = []

    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=24)

    for minutes in range(0, 60 * 24, 5):
        timestamp = start + timedelta(minutes=minutes)
        for vital in vital_type:
            reading = generate_reading(patient, vital)
            reading["timestamp"] = timestamp
            readings.append(reading)
    
    return readings
        


    
    


if __name__ == "__main__":
    conn = psycopg2.connect(**DB_CONFIG)
    logger.info("Connected to database")
    seed_patients(conn)
    conn.close()