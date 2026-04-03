"""Kafka producer that generates synthetic vital signs."""

import json
import logging
import random
import time
from datetime import datetime, timezone
from typing import Any

from confluent_kafka import Producer

from generator.src.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    NUM_PATIENTS,
    PRODUCE_INTERVAL_SECONDS,
    VITAL_TOPICS,
)
from generator.src.patient_profiles import generate_patient_profiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_producer() -> Producer:
    """Create and return a Kafka producer instance."""
    config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "client.id": "vitalstream-generator",
    }
    logger.info("Creating Kafka producer with servers: %s", KAFKA_BOOTSTRAP_SERVERS)
    return Producer(config)


def generate_reading(patient: dict[str,Any], vital_type: str) -> dict[str,Any]:
    """Generate a single vital sign reading for a patient.

    Uses the patient's baseline mean and standard deviation
    to produce a realistic value via Gaussian distribution.

    Args:
        patient: Patient profile dictionary with baselines.
        vital_type: Which vital sign to generate.

    Returns:
        Dictionary with patient_id, vital_type, value, unit, timestamp.
    """
    baseline = patient["baselines"][vital_type]
    value = random.gauss(baseline["mean"], baseline["std"])

    # Clamp values to physiological limits
    clamps = {
        "heart_rate": (30, 200),
        "blood_pressure_sys": (60, 250),
        "blood_pressure_dia": (40, 150),
        "spo2": (70, 100),
        "temperature": (34.0, 42.0),
        "resp_rate": (5, 45),
    }
    min_val, max_val = clamps[vital_type]
    value = max(min_val, min(max_val, value))

    return {
        "patient_id": patient["patient_id"],
        "vital_type": vital_type,
        "value": round(value, 1),
        "unit": baseline["unit"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def delivery_callback(err, msg):
    """Called once per message to confirm delivery or log errors."""
    if err is not None:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.debug(
            "Message delivered to %s [partition %d]",
            msg.topic(),
            msg.partition(),
        )


def run_producer() -> None:
    """Main loop: continuously produce vital signs for all patients."""
    patients = generate_patient_profiles(NUM_PATIENTS)
    producer = None
    max_tries=5

    for attempt in range(1, max_tries+1):
        try:
            producer= create_producer()
            
            producer.list_topics(timeout=5)
            logger.info(" Connected to Kafka at attempt %d", attempt)
            break
        
        except KeyboardInterrupt:
            logger.info("Shutting down during connection retry. ")
            return 
        
        except Exception as e:
            wait_time= 2** attempt
            logger.warning(
                "Kafka not available (attempt %d / %d): %s  Retrying in %ds",
                attempt,
                max_tries,
                e,
                wait_time,
            )
            try:
                time.sleep(wait_time)
            except KeyboardInterrupt:
                logger.info("Shutting down during conection retry.")
                return


    else:
        logger.error("Could not connect to Kafka after %d attempts. Exiting." , max_tries)
        return
    

    logger.info(
        "Starting vital signs generation for %d patients every %.1f seconds",
        len(patients),
        PRODUCE_INTERVAL_SECONDS,
    )

    try:
        while True:
            for patient in patients:
                for vital_type, topic in VITAL_TOPICS.items():
                    reading = generate_reading(patient, vital_type)
                    producer.produce(
                        topic=topic,
                        key=patient["patient_id"],
                        value=json.dumps(reading),
                        callback=delivery_callback,
                    )

                # Flush per patient to ensure messages are sent
                producer.flush()

            logger.info(
                "Produced readings for %d patients at %s",
                len(patients),
                datetime.now(timezone.utc).isoformat(),
            )

            time.sleep(PRODUCE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("Shutting down producer...")
    finally:
        producer.flush()
        logger.info("Producer shut down cleanly.")


if __name__ == "__main__":
    run_producer()