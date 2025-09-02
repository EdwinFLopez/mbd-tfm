#!/usr/bin/bash
set -eo pipefail

# Spark and Mongo connector coordinates
SC_GROUP="org.apache.spark"
SC_ARTIFACT="spark-connect_2.13"
SC_VERSION="4.0.0"
SC_MONGODB_GROUP="org.mongodb.spark"
SC_MONGODB_ARTIFACT="mongo-spark-connector_2.13"
SC_MONGODB_VERSION=10.5.0

# Spark Connect configs
SPARK_CONNECT="${SPARK_HOME}/sbin/start-connect-server.sh"
SPARK_CONNECT_PKGS="${SC_GROUP}:${SC_ARTIFACT}:${SC_VERSION}"
SPARK_CONNECT_PKGS="${SPARK_CONNECT_PKGS},${SC_MONGODB_GROUP}:${SC_MONGODB_ARTIFACT}:${SC_MONGODB_VERSION}"
SPARK_CONNECT_IVYOPTS="-Divy.home=${SPARK_HOME}/tmp -Divy.cache.dir=${SPARK_HOME}/tmp/cache"
SPARK_CONNECT_JAVAOPTS="spark.driver.extraJavaOptions='${SPARK_CONNECT_IVYOPTS}'"

# Update lookup path with spark execution path
export PATH="$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin"
export PYSPARK_PYTHON="/usr/bin/python3"

# Install python dependencies
SPARK_VENV="/usr/local/lib/python3.10/dist-packages"
sh -c "$(which pip3) install --no-cache-dir -t $SPARK_VENV --upgrade numpy"

# Launch Spark Connect
sh -c "${SPARK_CONNECT} --master ${SPARK_MASTER_URL} --conf '${SPARK_CONNECT_JAVAOPTS}' --packages ${SPARK_CONNECT_PKGS}" &
wait
