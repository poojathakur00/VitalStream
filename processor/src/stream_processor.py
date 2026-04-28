import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, min, max
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
TOPICS = "vitals.heart_rate,vitals.spo2,vitals.blood_pressure_dia,vitals.blood_pressure_sys,vitals.temperature,vitals.resp_rate"

schema = StructType([
    StructField("patient_id", StringType()),
    StructField("vital_type", StringType()),
    StructField("value", FloatType()),
    StructField("unit", StringType()),
    StructField("timestamp", StringType()),
])

def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("VitalStream")
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "org.postgresql:postgresql:42.6.0")
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

    windowed = (
        vitals
        .groupBy(
            window(col("timestamp"), "5 minutes"),
            col("patient_id"),
            col("vital_type")
        )
        .agg(
            avg("value").alias("avg_value"),
            min("value").alias("min_value"),
            max("value").alias("max_value")
        )
    )

    query = (
        windowed.writeStream
        .outputMode("update")
        .format("console")
        .option("truncate", False)
        .start()
    )

    logger.info("Stream processor running — waiting for data")
    query.awaitTermination()

if __name__ == "__main__":
    main()