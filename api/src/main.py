#!/usr/bin/env python
import os
from pyspark.sql import SparkSession

if __name__ == "__main__":
    sc_url = "sc://localhost:15002"
    mongo_url = "mongodb://localhost:27017/mbdtfmdb?directConnection=true"
    session = SparkSession.builder.appName("MBDTFM").remote(sc_url) \
            .config("spark.mongodb.read.connection.uri", mongo_url) \
            .config("spark.mongodb.write.connection.uri", mongo_url) \
            .getOrCreate()
    session.read.format("mongo").load()

    type(session)
    print(session)
    session.stop()
