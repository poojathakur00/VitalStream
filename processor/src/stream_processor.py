import logging
import json
import os
import psycopg2
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.functions import avg as spark_avg
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
from ews_scorer import calculate_ews

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
TOPICS = "vitals.heart_rate,vitals.spo2,vitals.blood_pressure_dia,vitals.blood_pressure_sys,vitals.temperature,vitals.resp_rate"

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "vitalstream"),
    "user": os.getenv("POSTGRES_USER", "vitalstream"),
    "password": os.getenv("POSTGRES_PASSWORD", "vitalstream_dev"),
}

schema = StructType([
    StructField("patient_id", StringType()),
    StructField("vital_type", StringType()),
    StructField("value", FloatType()),
    StructField("unit", StringType()),
    StructField("timestamp", StringType()),
])


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def write_ews_score(cursor, row, ews: dict):
    features = json.dumps({
        "heart_rate": row.heart_rate,
        "spo2": row.spo2,
        "bp_sys": row.blood_pressure_sys,
        "bp_dia": row.blood_pressure_dia,
        "temperature": row.temperature,
        "resp_rate": row.resp_rate,
    })
    cursor.execute("""
        INSERT INTO ews_scores
            (patient_id, score, risk_level, features, window_start, window_end)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        row.patient_id,
        ews["score"],
        ews["risk_level"],
        features,
        row.window.start,
        row.window.end,
    ))
    return cursor.fetchone()[0]


def write_alert(cursor, row, ews: dict, ews_score_id: int):
    cursor.execute("""
        INSERT INTO alerts
            (patient_id, ews_score_id, alert_type, severity, message)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        row.patient_id,
        ews_score_id,
        "THRESHOLD_BREACH",
        "CRITICAL" if ews["score"] >= 12 else "WARNING",
        f"EWS score {ews['score']} ({ews['risk_level']}) for patient {row.patient_id}",
    ))


def process_batch(batch_df, batch_id: int):
    rows = batch_df.collect()
    if not rows:
        return

    logger.info(f"Processing batch {batch_id} with {len(rows)} patients")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for row in rows:
            if row.patient_id is None:
                continue
            ews = calculate_ews(row)
            ews_score_id = write_ews_score(cursor, row, ews)
            if ews["score"] >= 5:
                write_alert(cursor, row, ews, ews_score_id)

        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Batch {batch_id} written to PostgreSQL")

    except Exception as e:
        logger.error(f"Failed to write batch {batch_id}: {e}")
        raise


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("VitalStream")
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "org.postgresql:postgresql:42.6.0")
        .config("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", "false")
        .getOrCreate()
    )


def main():
    logger.info("Starting VitalStream stream processor")
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    raw = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TOPICS)
        .option("startingOffsets", "latest")
        .load()
    )

    vitals = (
        raw
        .select(from_json(col("value").cast("string"), schema).alias("data"))
        .select("data.*")
        .withColumn("timestamp", col("timestamp").cast(TimestampType()))
        .withWatermark("timestamp", "1 minute")
    )

    pivoted = (
        vitals
        .groupBy(
            window(col("timestamp"), "5 minutes"),
            col("patient_id")
        )
        .pivot("vital_type", ["heart_rate", "spo2", "blood_pressure_sys",
                               "blood_pressure_dia", "temperature", "resp_rate"])
        .agg(spark_avg("value"))
    )

    query = (
        pivoted.writeStream
        .outputMode("complete")
        .foreachBatch(process_batch)
        .start()
    )

    logger.info("Stream processor running — waiting for data")
    query.awaitTermination()


if __name__ == "__main__":
    main()