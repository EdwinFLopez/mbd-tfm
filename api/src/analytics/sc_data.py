from pyspark.sql import SparkSession, DataFrame
from commons.constants import *


def load_products_collection(session: SparkSession) -> DataFrame:
    """
    Loads the MongoDB collection `mbdtfm_magento_catalog_products_mview` in r/w mode.
    :param session: Spark-Connect session instance
    :return: DataFrame
    """
    return __load_collection(session, MONGO_DATABASE, MONGO_PRODUCTS_COLLECTION)


def load_collection(session: SparkSession, collection: str) -> DataFrame:
    """
    Loads a given MongoDB collection in r/w mode.
    :param session: Spark-Connect session instance
    :param collection: MongoDB collection name
    :return: DataFrame
    """
    return __load_collection(session, MONGO_DATABASE, collection)


def __load_collection(session: SparkSession, database: str, collection: str) -> DataFrame:
    """
    Loads data from a mongodb collection through a Spark-Connect session in read/write mode.
    :param session: Spark-Connect session instance
    :param database: MongoDB database name
    :param collection: MongoDB collection name
    :return: DataFrame
    """
    df = (
        session.read.format("mongodb")
            .option("spark.mongodb.read.connection.uri", MONGO_URL)
            .option("spark.mongodb.write.connection.uri", MONGO_URL)
            .option("database", database)
            .option("collection", collection)
            .load()
    )
    return df
