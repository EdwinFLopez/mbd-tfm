#!/usr/bin/env python

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from urllib.parse import urlencode, quote_plus

def get_mongo_client() -> MongoClient:
    """Create a MongoDB client"""
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

def test_mongodb_connection():
    try:
        client = get_mongo_client()
        # Send a ping to the server to check if the connection is successful
        client.admin.command('ping')
        print("Connection to MongoDB is successful!")

    except ConnectionFailure:
        print("Failed to connect to MongoDB.")

if __name__ == "__main__":
    test_mongodb_connection()
