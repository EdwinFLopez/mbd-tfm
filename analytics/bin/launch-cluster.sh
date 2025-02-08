#!/usr/bin/bash
set -eo pipefail

# Prepare Spark Connect vars and command
SPARK_CONNECT_PACKAGES="$GROUP:$ARTIFACT:$VERSION"
IVY_OPTS="-Divy.home=$SPARK_HOME/tmp -Divy.cache.dir=$SPARK_HOME/tmp"
SPARK_CONNECT_JAVAOPT="spark.driver.extraJavaOptions='$IVY_OPTS'"
LOGS_DIR="/opt/spark/work-dir/data/logs"
export PATH="$SPARK_HOME/sbin:$PATH"

# Launch Master Node
#sh -c "start-master.sh" > $LOGS_DIR/spark-master.log 2>&1 &
sh -c "start-master.sh" &

# Launch Worker Node
#sh -c "start-worker.sh spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT" > $LOGS_DIR/spark-worker.log 2>&1 &
sh -c "start-worker.sh spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT" &

# Launch History Node
#sh -c "start-history-server.sh" > $LOGS_DIR/spark-history.log 2>&1 &
sh -c "start-history-server.sh" &

# Launch Spark Connect
#sh -c "start-connect-server.sh --conf '$SPARK_CONNECT_JAVAOPT' --packages $SPARK_CONNECT_PACKAGES" > $LOGS_DIR/spark-connect.log 2>&1 &
sh -c "start-connect-server.sh --conf '$SPARK_CONNECT_JAVAOPT' --packages $SPARK_CONNECT_PACKAGES" &

#sh -c "tail -f $LOGS_DIR/spark-master.log $LOGS_DIR/spark-worker.log $LOGS_DIR/spark-connect.log $LOGS_DIR/spark-history.log"
echo "Spark Services Up"
wait
