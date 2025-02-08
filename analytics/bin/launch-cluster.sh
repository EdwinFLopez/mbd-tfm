#!/usr/bin/bash
set -eo pipefail

# Prepare Spark Connect vars and command
export PATH="$SPARK_HOME/sbin:$PATH"

# Launch Master Node
#sh -c "start-master.sh" > $SPARK_LOG_DIR/spark-master.log 2>&1 &
sh -c "start-master.sh" &

# Launch Worker Node
#sh -c "start-worker.sh spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT" > $SPARK_LOG_DIR/spark-worker.log 2>&1 &
sh -c "start-worker.sh spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT" &

# Launch History Node
#sh -c "start-history-server.sh" > $SPARK_LOG_DIR/spark-history.log 2>&1 &
sh -c "start-history-server.sh" &

# Launch Spark Connect
#sh -c "start-connect-server.sh --conf '$SPARK_CONNECT_JAVAOPTS' --packages '$SPARK_CONNECT_PKGS'" > $SPARK_LOG_DIR/spark-connect.log 2>&1 &
sh -c "start-connect-server.sh --conf '$SPARK_CONNECT_JAVAOPTS' --packages '$SPARK_CONNECT_PKGS'" &

#sh -c "tail -f $SPARK_LOG_DIR/spark-master.log $SPARK_LOG_DIR/spark-worker.log $SPARK_LOG_DIR/spark-connect.log $SPARK_LOG_DIR/spark-history.log"
echo "Spark Services Up"
wait
