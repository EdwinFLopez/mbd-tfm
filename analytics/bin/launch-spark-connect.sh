#!/usr/bin/bash
set -eo pipefail

GROUP="${GROUP:-org.apache.spark}"
ARTIFACT="${ARTIFACT:-spark-connect_2.12}"
VERSION="${VERSION:-3.5.2}"

SPARK_CONNECT="$SPARK_HOME/sbin/start-connect-server.sh"
IVY_OPTS="-Divy.home=${SPARK_HOME}/tmp -Divy.cache.dir=${SPARK_HOME}/tmp"
SPARK_CONNECT_JAVAOPT="spark.driver.extraJavaOptions='${IVY_OPTS}'"

SPARK_CONNECT_PACKAGES="${GROUP}:${ARTIFACT}:${VERSION}"

echo "${SPARK_CONNECT} --conf '${SPARK_CONNECT_JAVAOPT}' --packages ${SPARK_CONNECT_PACKAGES}"
sh -c "${SPARK_CONNECT} --conf '${SPARK_CONNECT_JAVAOPT}' --packages ${SPARK_CONNECT_PACKAGES}"
