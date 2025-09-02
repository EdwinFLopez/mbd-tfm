from pyspark.sql import SparkSession, DataFrame
from commons.constants import MONGO_URL, MONGO_DATABASE


def save_collection(df: DataFrame, collection: str, mode: str = "overwrite") -> None:
    """
    Saves data to a mongodb collection through a Spark-Connect session in write mode,
    overwriting the stored data.

    :param df: DataFrame to save
    :param collection: MongoDB collection name
    :param mode: Save mode, default is "overwrite"
    """
    (   df.write
            .format("mongodb")
            .option("spark.mongodb.write.connection.uri", MONGO_URL)
            .option("database", MONGO_DATABASE)
            .option("collection", collection)
            .mode(mode)
            .save()
    )

def load_collection(session: SparkSession, collection: str) -> DataFrame:
    """
    Loads a given MongoDB collection in read-only mode.

    :param session: Spark-Connect session instance
    :param collection: MongoDB collection name
    :return: DataFrame
    """
    return (
        session.read
            .format("mongodb")
            .option("spark.mongodb.read.connection.uri", MONGO_URL)
            .option("database", MONGO_DATABASE)
            .option("collection", collection)
            .load()
    )
