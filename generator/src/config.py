import os


# Kafka
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")

# Number of synthetic patients to simulate
NUM_PATIENTS = int(os.getenv("NUM_PATIENTS", "20"))

# How often to produce readings (in seconds)
PRODUCE_INTERVAL_SECONDS = float(os.getenv("PRODUCE_INTERVAL_SECONDS", "1.0"))

# Kafka topics — one per vital type
VITAL_TOPICS = {
    "heart_rate": "vitals.heart_rate",
    "blood_pressure_sys": "vitals.blood_pressure_sys",
    "blood_pressure_dia": "vitals.blood_pressure_dia",
    "spo2": "vitals.spo2",
    "temperature": "vitals.temperature",
    "resp_rate": "vitals.resp_rate",
}