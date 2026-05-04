"""
Task 3 (Optional): Spark Structured Streaming to Kafka

What this script does:
1. Creates a Spark session with Kafka connector package.
2. Creates a Kafka sink for the input streaming DataFrame.
3. Writes static seller_id=7 data into input_data folder to trigger the stream.
4. Reads messages back from Kafka and prints samples for verification.

Supports both:
- Aiven Kafka (set SASL env vars)
- Local Docker Kafka (default PLAINTEXT localhost:9092)
"""

import os
import time
from typing import Dict

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, struct, to_json


DEFAULT_WINDOWS_BASE_DIR = r"C:\Users\KunalMajumdar\OneDrive - EPAM\EPAM Trainings\Spark for DQE"
DEFAULT_LINUX_BASE_DIR = "/home/jovyan"


def normalize_path_for_spark(path: str) -> str:
    """Return a Spark-friendly path across Windows and Linux runtimes."""
    if not path:
        return path

    # On Linux containers, convert a Windows drive path (C:\...) to /mnt/c/...
    if os.name != "nt" and len(path) > 2 and path[1] == ":":
        drive = path[0].lower()
        remainder = path[2:].lstrip("\\/").replace("\\", "/")
        return f"/mnt/{drive}/{remainder}"

    # Use forward slashes to avoid URI parsing issues in Spark.
    return path.replace("\\", "/")


def get_base_dir() -> str:
    from_env = os.getenv("BASE_DIR")
    if from_env:
        return normalize_path_for_spark(from_env)

    if os.name != "nt" and os.path.exists(DEFAULT_LINUX_BASE_DIR):
        return DEFAULT_LINUX_BASE_DIR

    return normalize_path_for_spark(DEFAULT_WINDOWS_BASE_DIR)


BASE_DIR = get_base_dir()
SALES_CSV_PATH = normalize_path_for_spark(os.path.join(BASE_DIR, "sales.csv"))
INPUT_DATA_PATH = normalize_path_for_spark(os.path.join(BASE_DIR, "input_data"))
CHECKPOINT_PATH = normalize_path_for_spark(os.path.join(BASE_DIR, "checkpoints", "kafka_sink"))

DEFAULT_KAFKA_BOOTSTRAP = "host.containers.internal:9092" if os.name != "nt" else "localhost:9092"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", DEFAULT_KAFKA_BOOTSTRAP)
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "topic-for-spark")
KAFKA_SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
KAFKA_SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", "PLAIN")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME", "")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD", "")

# Use explicit env override if needed; default matches current container Spark.
PYSPARK_VERSION = os.getenv("PYSPARK_VERSION", "3.5.0")
SPARK_KAFKA_PACKAGE = os.getenv(
    "SPARK_KAFKA_PACKAGE",
    f"org.apache.spark:spark-sql-kafka-0-10_2.12:{PYSPARK_VERSION}",
)


def kafka_auth_options() -> Dict[str, str]:
    options: Dict[str, str] = {
        "kafka.bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "kafka.security.protocol": KAFKA_SECURITY_PROTOCOL,
    }

    # If username/password are present, configure SASL auth.
    if KAFKA_USERNAME and KAFKA_PASSWORD:
        jaas = (
            "org.apache.kafka.common.security.plain.PlainLoginModule required "
            f'username="{KAFKA_USERNAME}" '
            f'password="{KAFKA_PASSWORD}";'
        )
        options["kafka.sasl.mechanism"] = KAFKA_SASL_MECHANISM
        options["kafka.sasl.jaas.config"] = jaas

    return options


def wait_for_stream_progress(query, timeout_seconds: int = 60) -> None:
    start = time.time()
    while time.time() - start <= timeout_seconds:
        progress = query.lastProgress
        if progress and int(progress.get("numInputRows", 0)) > 0:
            print(f"Streaming progress detected: {progress}")
            return
        time.sleep(2)
    print("No processed rows detected within timeout; continuing to verification step.")


def has_kafka_source(spark: SparkSession) -> bool:
    """Return True when Spark can resolve format('kafka')."""
    try:
        # Using localhost avoids slow DNS failures in containerized runtimes.
        (
            spark.read.format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "_probe_topic_")
            .load()
            .limit(0)
            .collect()
        )
        return True
    except Exception as exc:
        return "Failed to find data source: kafka" not in str(exc)


def create_spark_session_with_kafka() -> SparkSession:
    """Create/recreate SparkSession so kafka source is available."""
    active_spark = SparkSession.getActiveSession()
    if active_spark is not None and has_kafka_source(active_spark):
        return active_spark

    if active_spark is not None:
        print(
            "Active SparkSession has no Kafka connector. "
            "Attempting SparkSession restart with kafka package..."
        )
        active_spark.stop()
        time.sleep(2)

    spark = (
        SparkSession.builder.appName("Task3_Spark_Kafka")
        .config("spark.jars.packages", SPARK_KAFKA_PACKAGE)
        .getOrCreate()
    )

    if not has_kafka_source(spark):
        raise RuntimeError(
            "Kafka source is still unavailable after SparkSession restart. "
            "Restart the Jupyter kernel and run this first: \n"
            "import os\n"
            f"os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages {SPARK_KAFKA_PACKAGE} pyspark-shell'\n"
            "from pyspark.sql import SparkSession\n"
            "spark = SparkSession.builder.appName('Task3_Spark_Kafka').getOrCreate()\n"
            "Then run main() again."
        )

    return spark


def main() -> None:
    os.makedirs(INPUT_DATA_PATH, exist_ok=True)
    os.makedirs(CHECKPOINT_PATH, exist_ok=True)

    # Use a run-specific checkpoint to avoid stale offsets/state between retries.
    run_checkpoint_path = normalize_path_for_spark(
        os.path.join(CHECKPOINT_PATH, f"run_{int(time.time())}")
    )
    os.makedirs(run_checkpoint_path, exist_ok=True)

    print("=" * 80)
    print("Task 3: Spark Streaming -> Kafka")
    print("=" * 80)
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"SALES_CSV_PATH: {SALES_CSV_PATH}")
    print(f"INPUT_DATA_PATH: {INPUT_DATA_PATH}")
    print(f"KAFKA_BOOTSTRAP_SERVERS: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"KAFKA_TOPIC: {KAFKA_TOPIC}")
    print(f"KAFKA_SECURITY_PROTOCOL: {KAFKA_SECURITY_PROTOCOL}")
    print(f"RUN_CHECKPOINT_PATH: {run_checkpoint_path}")

    print(f"SPARK_KAFKA_PACKAGE: {SPARK_KAFKA_PACKAGE}")
    spark = create_spark_session_with_kafka()
    spark.sparkContext.setLogLevel("WARN")

    query = None
    try:
        if not os.path.exists(SALES_CSV_PATH):
            raise FileNotFoundError(
                "sales.csv was not found at "
                f"'{SALES_CSV_PATH}'. Set BASE_DIR to the folder containing sales.csv. "
                "Example for your container runtime: BASE_DIR=/home/jovyan"
            )

        # Static source DataFrame from Task 1.
        sales_df = spark.read.csv(SALES_CSV_PATH, header=True, inferSchema=True)
        seller7_df = sales_df.filter(col("seller_id") == 7)

        print(f"Loaded sales records: {sales_df.count():,}")
        print(f"seller_id=7 records: {seller7_df.count():,}")

        schema = sales_df.schema

        # Task 3.4: streaming DataFrame that watches input_data folder.
        streaming_df = (
            spark.readStream.format("csv")
            .schema(schema)
            .option("header", "true")
            .load(INPUT_DATA_PATH)
        )
        dedup_streaming_df = streaming_df.dropDuplicates(["order_id"])

        kafka_df = dedup_streaming_df.select(
            col("order_id").cast("string").alias("key"),
            to_json(struct(*[col(c) for c in dedup_streaming_df.columns])).alias("value"),
        )

        sink_options = kafka_auth_options()

        writer = (
            kafka_df.writeStream.format("kafka")
            .option("topic", KAFKA_TOPIC)
            .option("checkpointLocation", run_checkpoint_path)
            .outputMode("append")
            .trigger(processingTime="10 seconds")
        )

        for key, value in sink_options.items():
            writer = writer.option(key, value)

        query = writer.start()
        print(f"Started Kafka sink query. isActive={query.isActive}")

        # Task 3.5: write static data to input_data to trigger streaming ingestion.
        seller7_df.write.mode("append").option("header", "true").csv(INPUT_DATA_PATH)
        print("Wrote seller_id=7 static data to input_data folder.")

        # Block until currently available files are processed.
        query.processAllAvailable()

        stream_error = query.exception()
        if stream_error is not None:
            raise RuntimeError(f"Kafka sink query failed: {stream_error}")

        wait_for_stream_progress(query, timeout_seconds=60)

        # Task 3.6: pull messages from topic and verify transfer.
        kafka_reader = (
            spark.read.format("kafka")
            .option("subscribe", KAFKA_TOPIC)
            .option("startingOffsets", "earliest")
            .option("endingOffsets", "latest")
        )

        for key, value in sink_options.items():
            kafka_reader = kafka_reader.option(key, value)

        consumed_df = kafka_reader.load()

        total_messages = consumed_df.count()
        print(f"Kafka messages available in topic '{KAFKA_TOPIC}': {total_messages}")

        if total_messages > 0:
            consumed_df.selectExpr(
                "CAST(key AS STRING) AS key",
                "CAST(value AS STRING) AS value",
                "topic",
                "partition",
                "offset",
                "timestamp",
            ).show(20, truncate=False)
            print("Verification successful: streaming data was transferred to Kafka.")
        else:
            print("No messages found yet. Re-run script or wait a little and check topic again.")

    finally:
        if query is not None and query.isActive:
            query.stop()
        spark.stop()
        print("Stopped Spark session and streaming query.")


if __name__ == "__main__":
    main()
