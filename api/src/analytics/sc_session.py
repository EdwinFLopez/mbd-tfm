from pyspark.sql import SparkSession
from commons.constants import SPARK_CONNECT_URL


def get_session() -> SparkSession:
    """Gets or creates a Spark-Connect session."""
    return (
        SparkSession.builder
            .appName("MBD-TFM-APP")
            .config("spark.connect", "true")
            .remote(SPARK_CONNECT_URL)
            .getOrCreate()
    )
