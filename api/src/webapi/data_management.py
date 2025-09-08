import logging
import pandas as pd
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from pymongo.synchronous.collection import Collection
from commons.constants import (
    MONGO_URL, MONGO_DATABASE, MDB_EMBEDDINGS_COLLECTION
)

def reindex_search_indexes() -> pd.DataFrame:
    """
    Reindex all search indexes in embedding collection.
    """
    # subfunction ---------------------------------------------
    def _reindex_flat_props_index(emb_col: Collection) -> None:
        """
        Reindex full text search index for embeddings collection.
        """
        emb_col.update_search_index(
            name=f"{MDB_EMBEDDINGS_COLLECTION}_product_flat_props_idx",
            definition = {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                      "product_flat_props": {
                        "type": "string"
                      }
                    }
                }
            }
        )

    # subfunction ---------------------------------------------
    def _reindex_embeddings_index(emb_col: Collection) -> None:
        """
        Reindex vector search index for embeddings collection.
        Currently, the only way to reindex vector indexes
        is by dropping the index and creating a new one. UpdateSearchIndex
        operation doesn't support new vector indexes.
        """
        emb_col.drop_search_index(
            name=f"{MDB_EMBEDDINGS_COLLECTION}_product_embeddings_vector_idx"
        )
        vector_index_definition = {
            "fields": [{
                "type": "vector",
                "path": "product_embeddings",
                "numDimensions": 128,
                "similarity": "cosine",
                "quantization": "scalar"
            }]
        }

        # Create SearchIndexModel with type attribute set to "vectorSearch"
        emb_col.create_search_index(
            model=SearchIndexModel(
                name=f"{MDB_EMBEDDINGS_COLLECTION}_product_embeddings_vector_idx",
                definition=vector_index_definition,
                type="vectorSearch"
            )
        )

    # Implementation ------------------------------------------
    client: MongoClient = None
    try:
        client = MongoClient(MONGO_URL)
        with client:
            emb_col = client[MONGO_DATABASE][MDB_EMBEDDINGS_COLLECTION]
            _reindex_flat_props_index(emb_col)
            _reindex_embeddings_index(emb_col)
            data = list(emb_col.list_search_indexes())
            if not data:
                return pd.DataFrame()
            return pd.DataFrame(data)
    except Exception as e:
        logging.error(e)
        raise e from e
    finally:
        client.close()


def list_search_indexes() -> pd.DataFrame:
    """
    List all search indexes in embedding collection.
    """
    client: MongoClient = None
    try:
        client = MongoClient(MONGO_URL)
        with client:
            col = client[MONGO_DATABASE][MDB_EMBEDDINGS_COLLECTION]
            data = list(col.list_search_indexes())
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(e)
        raise e from e
    finally:
        client.close()


def get_data(query: str) -> pd.DataFrame:
    """
    Get data from MongoDB.
    """
    if query != "":
        with MongoClient(MONGO_URL) as client:
            db = client[MONGO_DATABASE]
            collection = db[MDB_EMBEDDINGS_COLLECTION]
            cursor = collection.aggregate(
                pipeline=[{
                    "$search": {
                        "index": f"{MDB_EMBEDDINGS_COLLECTION}_product_flat_props_idx",
                        "text": {"query" : query, "path": "product_flat_props"}
                    }
                }]
            )
            data = cursor.to_list()
        if data:
            return pd.DataFrame(data)
    return pd.DataFrame()


def get_recommendations(sku: str) -> pd.DataFrame:
    """
    Get recommendations from MongoDB using vector search over product_embeddings.
        1. Find given product by sku and read its embeddings field. If not found or
           no embeddings, fail.
        2. Create the search query pipeline to find the recommendations by the record's
           embeddings.
       3. Return the first 20 recommendations for the given product.

    Args:
        sku (str): The product sku to search for recommendations for.

    Returns:
        pd.DataFrame: The recommendations for the given product.
    """
    with MongoClient(MONGO_URL) as client:
        db = client[MONGO_DATABASE]
        collection = db[MDB_EMBEDDINGS_COLLECTION]
        product = collection.find({"product_sku": sku}).to_list(1)

        if not product or len(product) == 0:
            return pd.DataFrame()

        vector_search_pipeline = [{
            "$vectorSearch": {
                "index" : f"{MDB_EMBEDDINGS_COLLECTION}_product_embeddings_vector_idx",
                "path": "product_embeddings",
                "queryVector": product[0]['product_embeddings'],
                "numCandidates": 20,
                "limit": 20,
            }
        },{
            "$project": {
                "_id": 1,
                "product_sku": 1,
                "product_name": 1,
                "product_properties": 1,
                "product_embeddings": 1,
                "product_created_at": 1,
                "product_updated_at": 1,
                "product_deleted_at": 1,
                "embeddings_updated_at": 1,
                "similarity_score": {
                    "$meta": "vectorSearchScore"
                }
            }
        },{
            "$sort": {
                "similarity_score": -1
            }
        }]

        cursor = collection.aggregate(pipeline=vector_search_pipeline)
        data = cursor.to_list()
        if data:
            return pd.DataFrame(data)
    return pd.DataFrame()


def _dummy_data() -> pd.DataFrame:
    """
    Dummy data for testing purposes.
    """
    return pd.DataFrame({
        "product_sku": ["24-MB04", "24-MB05", "24-MB05"],
        "product_name": ["Red Shoes", "Blue Hat", "Green Shirt"],
        "product_properties": [
            "{\"product_sku\":\"24-MB04\",\"product_type\":\"simple\",\"product_ratings\":4.5000,\"product_categories\":[\"Gear\",\"Collections\"],\"product_ratings_pct\":90.0000,\"product_attribute_set\":\"Bag\"}",
            "{\"product_sku\":\"24-MB05\",\"product_type\":\"simple\",\"product_ratings\":4.5000,\"product_categories\":[\"Gear\",\"Collections\"],\"product_ratings_pct\":90.0000,\"product_attribute_set\":\"Bag\"}",
            "{\"product_sku\":\"24-MB06\",\"product_type\":\"simple\",\"product_ratings\":4.5000,\"product_categories\":[\"Gear\",\"Collections\"],\"product_ratings_pct\":90.0000,\"product_attribute_set\":\"Bag\"}"
        ]
    })