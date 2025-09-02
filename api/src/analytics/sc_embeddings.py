from commons.constants import MDB_PRODUCTS_COLLECTION_URL
import json
from pyspark.ml.feature import Tokenizer, HashingTF, IDF
from pyspark.sql import DataFrame
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType
from typing import Dict


def create_product_embeddings(df: DataFrame, properties_column: str = "product_properties", embeddings_column: str = "product_embeddings") -> None:
    """
    Reads products from MongoDB, calculates embeddings for the `product_properties`
    field in collection `mbdtfm_magento_catalog_products_mview`, and writes back to MongoDB
    with the new `product_embeddings` column in the same collection.
    :param df: DataFrame containing the `product_properties` column to create embeddings from.
    :param properties_column: Name of the `product_properties` column to create embeddings from.
    :param embeddings_column: Name of the `product_embeddings` column to create embeddings to.
    :return: None.
    """
    flatten_udf = udf(__flatten_json, StringType())
    df_flat = df.withColumn(f"{properties_column}_flat", flatten_udf(col(properties_column)))
    # Note: dataframe `df` must be open in R/W mode
    source_column = f"{properties_column}_flat"
    df = __compute_embeddings(df_flat, embeddings_column, source_column)
    df.write.format("mongo").option("uri", MDB_PRODUCTS_COLLECTION_URL).mode("overwrite").save()


def __compute_embeddings(df: DataFrame, target_column: str, source_column: str) -> DataFrame:
    tokenizer = Tokenizer(inputCol=source_column, outputCol="tokens")
    tokenized = tokenizer.transform(df)
    hashing_tf = HashingTF(inputCol="tokens", outputCol="rawFeatures", numFeatures=128)
    featurized = hashing_tf.transform(tokenized)
    idf = IDF(inputCol="rawFeatures", outputCol=target_column)
    idf_model = idf.fit(featurized)
    return idf_model.transform(featurized)


def __flatten_json(json_str: str) -> str:
    try:
        flat = __flatten(json.loads(json_str))
        return ' '.join([f"{k}={v}" for k, v in flat.items()])
    except Exception:
        return ''


def __flatten(obj: Dict, prefix: str = '') -> Dict[str, str]:
    """
    Recursive helper to flatten JSON objects inside a UDF, preparing data for tokenization.
    :param obj: JSON object.
    :param prefix: prefix to prepend to all keys.
    :return: flattened dictionary.
    """
    items = []
    for k, v in obj.items():
        new_key = f"{prefix}{k}" if prefix == '' else f"{prefix}.{k}"
        if isinstance(v, dict):
            items.extend(__flatten(v, new_key).items()) # Recursive call.
        elif isinstance(v, list):
            val_str = ' '.join([str(item) for item in v])
            items.append((new_key, val_str))
        else:
            items.append((new_key, str(v)))
    return dict(items)
