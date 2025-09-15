#!/usr/bin/env python
import requests
import os
from pymongo import MongoClient

def get_mongo_client_with_auth() -> MongoClient:
    """Create a MongoDB client using authentication data for the admin user"""
    mdb = {
        "usr"       : 'mbdtfm_admin',
        "pwd"       : 'mbdtfm_pwd$$',
        "db"        : 'mbdtfm_db',
        "authSource": 'admin',
        "host"      : 'localhost',
        "port"      : 27017
    }
    mongodb_uri = "mongodb://{usr}:{pwd}@{host}:{port}/{db}?authSource={authSource}".format(**mdb)
    return MongoClient(mongodb_uri)

def get_mongo_client() -> MongoClient:
    """Create a MongoDB client"""
    if "MONGO_DB_URL" in os.environ.keys():
        mongodb_uri = os.environ['MONGO_DB_URL']
    else:
        mdb = {
            "db"        : 'mbdtfmdb',
            "host"      : 'localhost',
            "port"      : 27017
        }
        mongodb_uri = "mongodb://{host}:{port}/{db}".format(**mdb)
    return MongoClient(mongodb_uri)

def test_mongodb_connection(with_auth : bool = False):
    """Test if MongoDB connection is up and working"""
    try:
        client = get_mongo_client_with_auth() if with_auth else get_mongo_client()
        # Send a ping to the server to check if the connection is successful
        client.admin.command('ping')
        print(f"Connection to MongoDB {'with auth' if with_auth else ''} Ok")

    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")


def test_url_is_working(url: str) -> str:
    """Test if a given URL is working"""
    try:
        response = requests.get(url)
        # Check if the response status code is 200 (OK)
        return "Ok" if response.status_code == 200  else f"Failed with status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Failed with error Error: {str(e)}"


def test_spark_cluster_connections():
    """Test if all nodes of a spark cluster are working"""
    spark_nodes = {
        "Spark History": "http://localhost:18080",
        "Spark Master": "http://localhost:8080",
        "Spark Connect": "http://localhost:4040",
        "Spark Worker": "http://localhost:8081",
    }
    spark_vars = ["SPARK_MASTER_URL", "SPARK_WORKER_URL", "SPARK_HISTORY_URL", "SPARK_CONNECT_URL"]
    if all(key in os.environ.keys() for key in spark_vars):
        spark_nodes = {
            "Spark Master": os.environ.get("SPARK_MASTER_URL"),
            "Spark Worker": os.environ.get("SPARK_WORKER_URL"),
            "Spark History": os.environ["SPARK_HISTORY_URL"],
            "Spark Connect": os.environ["SPARK_CONNECT_URL"]
        }
    for key in spark_nodes.keys():
        print(f"Connection to {key}: {test_url_is_working(spark_nodes[key])}")


if __name__ == "__main__":
    test_mongodb_connection(with_auth=False)
    test_spark_cluster_connections()
