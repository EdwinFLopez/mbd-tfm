import os

# ###############################################################
# Spark connect required environment variables and default values
SPARK_CONNECT_HOST = os.getenv("SPARK_CONNECT_HOST", "spark-connect")
SPARK_CONNECT_PORT = int(os.getenv("SPARK_CONNECT_PORT", 15002))
SPARK_CONNECT_URL = f"sc://{SPARK_CONNECT_HOST}:{SPARK_CONNECT_PORT}"
# ###############################################################

# ###############################################################
# MongoDb required environment variables and default values
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb-atlas")
MONGO_PORT = int(os.getenv("MONGO_HOST", 27017))
MONGO_URL = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
# ###############################################################

# ###############################################################
# Some mongodb constants for the views and their url.
MONGO_DATABASE = "mbdtfmdb"
MDB_PRODUCTS_COLLECTION = "mbdtfm_magento_catalog_products_mview"
MDB_EMBEDDINGS_COLLECTION = "mbdtfm_magento_catalog_products_embeddings"
MDB_PRODUCTS_COLLECTION_URL = f"{MONGO_URL}/{MONGO_DATABASE}.{MDB_PRODUCTS_COLLECTION}"
MDB_EMBEDDINGS_COLLECTION_URL = f"{MONGO_URL}/{MONGO_DATABASE}.{MDB_EMBEDDINGS_COLLECTION}"
# ###############################################################

# ###############################################################
# Separator used to split words in the source text when creating
# embeddings.
WORD_SEPARATOR: str = ";;;;;"
# ###############################################################
