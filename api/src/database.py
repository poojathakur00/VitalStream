import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "vitalstream"),
    "user": os.getenv("POSTGRES_USER", "vitalstream"),
    "password": os.getenv("POSTGRES_PASSWORD", "vitalstream_dev"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)