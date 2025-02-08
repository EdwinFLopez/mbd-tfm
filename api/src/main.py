#!/usr/bin/env python
import os

from pyspark.sql import SparkSession

def get_spark_session(sc_url: str) -> SparkSession:
    return SparkSession.builder.remote(sc_url).appName("MBDTFM").getOrCreate()

if __name__ == "__main__":
    sc_url = os.environ["SPARK_CONNECT_URL"].replace("http:", "sc:")
    with get_spark_session(sc_url) as session:
        type(session)
        print(session)
        session.stop()
    print("Running!")
