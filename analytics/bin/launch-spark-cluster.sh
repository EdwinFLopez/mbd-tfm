#!/usr/bin/bash
set -eo pipefail

# Update lookup path with spark execution path
export PATH="$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH"

# Launch Master Node
sh -c "start-master.sh" &

# Launch Worker Node
sh -c "start-worker.sh ${SPARK_MASTER_URL}" &

# Launch History Node
sh -c "start-history-server.sh" &

echo "Spark Cluster Up"
wait
