from pyspark.sql import SparkSession
from commons.constants import SPARK_CONNECT_URL


def get_session() -> SparkSession:
    """Gets or creates a Spark-Connect session."""
    return __get_or_create_session(SPARK_CONNECT_URL)


def __get_or_create_session(spark_connect_url: str) -> SparkSession:
    """
    Creates a Spark-Connect session with a given host and port.
    :param sc_host: Hostname of the Spark Connect server
    :param sc_port: Port of the Spark Connect server
    :return: SparkSession
    """
    session = (
        SparkSession.builder
            .appName("MBD_TFM_APP")
            .config("spark.connect", "true")
            .remote(spark_connect_url)
            .getOrCreate()
    )
    return session
