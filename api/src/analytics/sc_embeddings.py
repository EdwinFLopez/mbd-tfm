import json
import re
from pyspark.ml import Pipeline
from pyspark.ml.feature import Word2Vec, Normalizer
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    udf, col, split, coalesce, to_timestamp,
    lit, greatest, current_timestamp
)
from pyspark.sql.types import StringType, ArrayType, FloatType
from analytics.sc_data import load_collection, save_collection
from commons.constants import (
    MDB_PRODUCTS_COLLECTION, MDB_EMBEDDINGS_COLLECTION, WORD_SEPARATOR
)

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
        8. Merge the new embeddings with existing products in the embeddings dataframe,
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

    # UDF defined inside the function to avoid serialization
    # issues with spark-connect.
    def __escape_value(value: str) -> str:
        """
        Escapes special characters in values:
            1) quotes with escaped quotes,
            2) replace newlines and tabs with spaces
            3) remove HTML tags
        Args:
            value: String to escape
        Returns:
            Escaped string safe for embedding
        """

        value = value.replace('"', '\\"')
        value = ' '.join(value.split())
        value = re.sub(r'<[^>]+>', '', value)
        return value.strip()

    # UDF defined inside the function to avoid serialization issues
    # with spark-connect.
    def __flatten_json_nr(json_str: str) -> str:
        """
        Converts a JSON string to flattened key-value pairs with enclosed values.
        Args:
            json_str: JSON string to flatten.
        Returns:
            Flattened string with key="escaped_value" pairs separated by ';;;;;'.
        """
        try:
            obj = json.loads(json_str)
            flat = {}
            stack = [(obj, '')]
            while stack:
                current, prefix = stack.pop()
                if isinstance(current, dict):
                    for k, v in current.items():
                        new_key = f"{prefix}{k}" if prefix == '' else f"{prefix}.{k}"
                        stack.append((v, new_key))
                elif isinstance(current, (list, tuple, set)):
                    escaped_items = [__escape_value(str(x)) for x in current if x]
                    flat[prefix] = WORD_SEPARATOR.join(escaped_items)
                elif current is not None:
                    flat[prefix] = __escape_value(str(current))
            pairs = [f'{k}="{v}"' for k, v in flat.items() if v]
            return WORD_SEPARATOR.join(pairs)
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            print(f"Error flattening JSON: {e}")
        return ''

    try:
        # Name of the column with JSON product properties.
        PROPERTIES_COLUMN = "product_properties"
        # Name of the column to store embeddings.
        EMBEDDINGS_COLUMN = "product_embeddings"
        # Name of the column to store flattened properties.
        FLAT_PROPS_COLUMN = "product_flat_props"
        # Name of the column to store embeddings update timestamp.
        PROCESS_TS_COLUMN = "embeddings_updated_at"

        # Load collections -----------------------------------------------------*
        products_df = load_collection(session, MDB_PRODUCTS_COLLECTION).cache()
        embeddings_df = load_collection(session, MDB_EMBEDDINGS_COLLECTION)

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

        # Check if there are candidates to process ------------------------------*
        if len(candidates_df.select("_id.product_id").limit(1).collect()) == 0:
            print("No products found for updating embeddings.")
            return

        # UDF to Flatten JSON properties: transforms json to escaped -----------*
        # key="value" pairs.
        # Stores the result in a new column named `product_flat_props`
        # Note: This field will be used to generate embeddings.
        flatten_udf = udf(__flatten_json_nr, StringType())

        # Generate embeddings into column `product_embeddings` -----------------*
        # using the flattened properties column as source.
        # Add a processing timestamp column `embeddings_updated_at`.
        products_embeddings_df = __compute_embeddings(
            candidates_df
                .withColumn(FLAT_PROPS_COLUMN, flatten_udf(col(PROPERTIES_COLUMN)))
                .withColumn(PROCESS_TS_COLUMN, current_timestamp()),
            EMBEDDINGS_COLUMN,
            FLAT_PROPS_COLUMN
        ).cache()


        # Merge results with existing products into ----------------------------*
        # products_embeddings table.
        final_products_with_embeddings_df = products_df.alias("p").join(
            products_embeddings_df.select("_id", FLAT_PROPS_COLUMN, EMBEDDINGS_COLUMN, PROCESS_TS_COLUMN),
            ["_id"],
            "left_outer"
        ).select(
            "p.*",    # All original columns
            col(FLAT_PROPS_COLUMN), # Flattened properties
            col(EMBEDDINGS_COLUMN), # Embeddings vector
            col(PROCESS_TS_COLUMN)  # Timestamp of embedding generation
        ).cache()

        # Write back to MongoDB ------------------------------------------------*
        save_collection(final_products_with_embeddings_df, MDB_EMBEDDINGS_COLLECTION)
        print(f"Successfully wrote embeddings to MongoDB into {MDB_EMBEDDINGS_COLLECTION}")
    except Exception as edb:
        print(f"Error writing embeddings: {edb}")
        raise Exception(f"Could not write embeddings to MongoDB: {str(edb)}") from edb
    finally:
        # Release cached DataFrames --------------------------------------------*
        to_release = []
        if 'products_df' in locals() and products_df is not None:
            to_release.append(products_df)
        if 'candidates_df' in locals() and candidates_df is not None:
            to_release.append(candidates_df)
        if 'products_embeddings_df' in locals() and products_embeddings_df is not None:
            to_release.append(products_embeddings_df)
        if 'final_products_with_embeddings_df' in locals() and final_products_with_embeddings_df is not None:
            to_release.append(final_products_with_embeddings_df)
        for df in to_release:
            try:
                df.unpersist()
            except Exception as eps:
                print(f"Error unpersisting DataFrame: {eps}")
            finally:
                session.catalog.clearCache()


def __compute_embeddings(
    source_df: DataFrame,
    target_column: str,
    source_column: str
) -> DataFrame:
    """
    Computes Word2Vec embeddings from a source text column in a DataFrame.

    Args:
        source_df: Input DataFrame containing the source text column.
        target_column: Name of the column to store the resulting embeddings.
        source_column: Name of the source text column to process.

    Returns:
        DataFrame with an additional column containing the embeddings and the flat properties.
    """


    # It has to be defined inside the function to avoid serialization
    # issues with spark-connect.
    def __values_to_array_udf(v) -> list[float]:
        """
        Converts a Spark MLlib vector to a Python list.
        If the vector is None, returns a list of 128 zeros.
        Args:
            v: Spark MLlib vector or None.
        Returns:
            List of floats representing the vector or a list of 128 zeros.
        """
        return v.toArray().tolist() if v is not None else [128 * 0.0]

    # Intermediate column where the words array is stored.
    WORDS_COLUMN = "words"
    # Intermediate column for calculating features.
    FEATURES_COLUMN = "features"
    # Intermediate column for normalized features.
    NORMALIZED_FEATURES_COLUMN = "normalized_features"

    # Split flattened text column into words column and cache the resulting df
    df_flattened_with_words = source_df.withColumn(
        WORDS_COLUMN,
        split(col(source_column), WORD_SEPARATOR)
    ).cache()

    # Initialize Word2Vec + Normalize model pipeline
    pipeline = Pipeline(stages=[
        # Configure Word2Vec with 128 dimensions
        Word2Vec(
            vectorSize=128,
            minCount=0,
            inputCol=WORDS_COLUMN,
            outputCol=FEATURES_COLUMN,
            windowSize=10,
            maxSentenceLength=4000
        ),
        # Add feature normalizer to keep vector magnitudes consistent
        Normalizer(
            inputCol=FEATURES_COLUMN,
            outputCol=NORMALIZED_FEATURES_COLUMN,
            p=2.0
        )
    ])

    # Apply transformations:
    # Fit and transform model to get word vectors
    # Normalize vectors
    model = pipeline.fit(df_flattened_with_words)
    transformed_df = model.transform(df_flattened_with_words)

    # UDF to convert Spark MLlib vector to Python array,
    # suitable for JSON serialization and storage in MongoDB
    to_array_udf = udf(__values_to_array_udf, ArrayType(FloatType()))

    df_result = (
        transformed_df
            # Extract array from features vector into target column
            .withColumn(target_column, to_array_udf(col(FEATURES_COLUMN)))
            # remove intermediate columns
            .drop(WORDS_COLUMN, FEATURES_COLUMN, NORMALIZED_FEATURES_COLUMN)
    )
    return df_result
