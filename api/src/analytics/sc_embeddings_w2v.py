#%%
import json
import re
from analytics.sc_data import load_collection, save_collection
from commons.constants import MDB_PRODUCTS_COLLECTION, MDB_EMBEDDINGS_COLLECTION
from typing import Dict
from pyspark.ml.feature import Word2Vec, Normalizer
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    udf, col, split, coalesce, to_timestamp,
    lit, greatest, current_timestamp
)
from pyspark.sql.types import StringType, ArrayType, FloatType


def create_product_embeddings_w2v(session: SparkSession) -> None:
    """
    Reads products from MongoDB collection `mbdtfm_magento_catalog_products_mview` using
    a spark-connect session; calculates embeddings for the `product_properties` field
    into `product_embeddings` column, and writes it back to MongoDB into collection
    `mbdtfm_magento_catalog_products_embeddings`, updating existing records.

    Only products with updated `product_updated_at` timestamps are processed, the rest are
    inserted as is into the embeddings collection.

    The process to calculate the embeddings is as follows:
        1. Load products and existing embeddings from MongoDB.
        2. Select products needing updates by comparing `product_updated_at` with the
           existing `embeddings_updated_at` timestamp.
        3. Flatten the JSON in `product_properties` into key="escaped_value" pairs separated
           by ';;;;;'. The result is stored in a new column `product_flat_props`.
        4. Split the flattened text into words using ';;;;;' as separator to be used as the
           words entry for the word2vec model.
        5. Use Word2Vec to compute 128-dimensional embeddings from the words input.
        6. Normalize the embeddings to have consistent magnitudes.
        7. Store the resulting embeddings in `product_embeddings` column, and the current
           timestamp in `embeddings_updated_at`.
        8. Merge the new embeddings with existing products in the embeddings collection,
           updating only those that have changed.
        9. Write the final DataFrame back to MongoDB, overwriting the existing data in the
           embeddings collection `mbdtfm_magento_catalog_products_embeddings`.
        10. Release cached DataFrames to free memory.

    Args:
        session: Spark-Connect session instance.
    Returns:
        None.
    Raises:
        Exception: If any error occurs during the process.
    """
    # products_collection: MongoDB collection name for products.
    products_collection: str = MDB_PRODUCTS_COLLECTION,
    # embeddings_collection: MongoDB collection name for embeddings.
    embeddings_collection: str = MDB_EMBEDDINGS_COLLECTION,
    # properties_column: Name of the column with JSON product properties.
    properties_column: str = "product_properties",
    # embeddings_column: Name of the column to store embeddings.
    embeddings_column: str = "product_embeddings",
    # flat_props_column: Name of the column to store flattened properties.
    flat_props_column: str = "product_flat_props",
    # process_ts_column: Name of the column to store embeddings update timestamp.
    process_ts_column: str = "embeddings_updated_at"
    try:
        # Load collections -----------------------------------------------------*
        products_df = load_collection(session, products_collection).cache()
        embeddings_df = load_collection(session, embeddings_collection).cache()

        # Select products needing updates: -------------------------------------*
        # Join and filter where new.product_updated_at is newer
        # than embeddings last update ts or old.updated_at

        # Default timestamp for comparison
        default_ts = to_timestamp(lit("1900-01-01 00:00:00"))
        candidates_df = (
            products_df.alias("p").join(
                embeddings_df.alias("e"),
                col("p._id.product_id") == col("e._id.product_id"),
                "left"
            )
        ).filter(
            col("p.product_updated_at") > greatest(
                coalesce(col("e.product_updated_at"), default_ts),
                coalesce(col("e.embeddings_updated_at"), default_ts)
            )
        ).select("p.*").cache()

        # UDF to Flatten JSON properties: transforms json to escaped -----------*
        # key="value" pairs.
        # Stores the result in a new column named `product_flat_props`
        # Note: This field will be used to generate embeddings from.
        flatten_udf = udf(__flatten_json, StringType())
        flatten_candidates_df = candidates_df.withColumn(
            flat_props_column, flatten_udf(col(properties_column))
        ).cache()

        # Generate embeddings into column `product_embeddings` -----------------*
        # using the flattened properties column as source.
        # Add a processing timestamp column `embeddings_updated_at`.
        products_embeddings_df = __compute_embeddings(
            flatten_candidates_df, embeddings_column, flat_props_column
        ).withColumn(process_ts_column, current_timestamp()).cache()

        # Merge results with existing products into ----------------------------*
        # products_embeddings table.
        final_products_with_embeddings_df = products_df.alias("p").join(
            products_embeddings_df.select(
                "_id", flat_props_column, embeddings_column, process_ts_column
            ),
            ["_id"],
            "left_outer"
        ).select(
            "p.*",    # All original columns
            col(flat_props_column), # Flattened properties
            col(embeddings_column), # Embeddings vector
            col(process_ts_column)  # Timestamp of embedding generation
        ).cache()

        # Write back to MongoDB ------------------------------------------------*
        try:
            save_collection(final_products_with_embeddings_df, embeddings_collection)
            print(f"Successfully wrote embeddings to MongoDB into {embeddings_collection}")
        except Exception as edb:
            print(f"Error writing to MongoDB: {edb}")
            raise Exception(f"Could not write embeddings to MongoDB: {str(edb)}")

        finally:
            # Release cached DataFrames --------------------------------------------*
            dfs = [
                products_df, embeddings_df, candidates_df,
                products_embeddings_df, flatten_candidates_df,
                final_products_with_embeddings_df
            ]
            for df in dfs:
                try:
                    df.unpersist()
                except Exception as eps:
                    print(f"Error unpersisting DataFrame: {eps}")
                finally:
                    session.catalog.clearCache()

    except Exception as e:
        print(f"Error in create_product_embeddings: {e}")
        raise Exception(f"Could not create embeddings {str(e)}")


def __compute_embeddings(
    source_df: DataFrame,
    target_column: str,
    source_column: str,
    word_separator = ";;;;;"
) -> DataFrame:
    """
    Computes Word2Vec embeddings from a source text column in a DataFrame.

    Args:
        source_df: Input DataFrame containing the source text column.
        target_column: Name of the column to store the resulting embeddings.
        source_column: Name of the source text column to process.
        word_separator: Separator used to split words in the source text.

    Returns:
        DataFrame with an additional column containing the embeddings and the flat properties.
    """

    words_column = "words"
    features_column = "features"
    normalized_features_column = "normalized_features"

    # Split flattened text into words
    df_words = source_df.withColumn(
        words_column, split(col(source_column), word_separator)
    ).cache()

    # Configure Word2Vec with 128 dimensions
    word_to_vec_model = Word2Vec(
        vectorSize=128,
        minCount=0,
        inputCol=words_column,
        outputCol=features_column,
        windowSize=5,
        maxSentenceLength=2000
    )

    # Add feature normalizer to keep vector magnitudes consistent
    normalizer = Normalizer(
        inputCol=features_column,
        outputCol=normalized_features_column,
        p=2.0
    )

    # Fit and transform model to get word vectors
    model = word_to_vec_model.fit(df_words)

    # UDF to convert Spark MLlib vector to Python array,
    # suitable for JSON serialization and storage in MongoDB
    extract_values_udf = udf(lambda v: v.toArray().tolist(), ArrayType(FloatType()))

    # Apply transformations and cleanup intermediate columns, normalizing the vectors
    return (
        normalizer.transform(model.transform(df_words))
            .withColumn(target_column, extract_values_udf(col(features_column)))
            .drop(words_column, features_column, normalized_features_column)
    )

def __flatten_json(json_str: str, word_separator: str=';;;;') -> str:
    """
    Converts a JSON string to flattened key-value pairs with enclosed values.

    Args:
        json_str: JSON string to flatten.
        word_separator: Separator for key-value pairs. Default is ';;;;'

    Returns:
        String-separated string of key="escaped_value" pairs
    """
    if not json_str:
        return ''

    try:
        flat = __flatten(json.loads(json_str))
        # Enclose values in quotes and escape internal quotes
        pairs = [f'{k}="{v}"' for k, v in flat.items() if v]
        return word_separator.join(pairs)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return ''

def __flatten(obj: Dict, prefix: str = '', word_separator: str = ';;;;') -> Dict[str, str]:
    """
    Recursively flattens a nested dictionary with value escaping.

    Args:
        obj: Dictionary to flatten
        prefix: Key prefix for nested items

    Returns:
        Flattened dictionary with escaped values
    """
    items = []
    for k, v in obj.items():
        new_key = f"{prefix}{k}" if prefix == '' else f"{prefix}.{k}"

        if isinstance(v, dict):
            items.extend(__flatten(v, new_key).items())
        elif isinstance(v, (list, tuple, set)):
            # Join array items and escape special chars
            escaped_items = [__escape_value(str(x)) for x in v if x]
            items.append((new_key, word_separator.join(escaped_items)))
        elif v is not None:
            items.append((new_key, __escape_value(str(v))))

    return dict(items)

def __escape_value(value: str) -> str:
    """
    Escapes special characters in values.

    Args:
        value: String to escape

    Returns:
        Escaped string safe for embedding
    """
    # Replace quotes with escaped quotes
    value = value.replace('"', '\\"')

    # Replace newlines and tabs with spaces
    value = ' '.join(value.split())

    # Remove HTML tags
    value = re.sub(r'<[^>]+>', '', value)
    return value.strip()