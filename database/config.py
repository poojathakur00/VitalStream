"""Shared PostgreSQL configuration."""

import os

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "vitalstream"),
    "user": os.getenv("POSTGRES_USER", "vitalstream"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}