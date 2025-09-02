#!/usr/bin/bash
set -eo pipefail

# Update lookup path with spark execution path
export PATH="$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin"
export PYSPARK_PYTHON="/usr/bin/python3"

# Install python dependencies
SPARK_VENV="/usr/local/lib/python3.10/dist-packages"
sh -c "$(which pip3) install --no-cache-dir -t $SPARK_VENV --upgrade numpy"

# Launch Master Node
sh -c "start-master.sh" &

# Launch Worker Node
sh -c "start-worker.sh ${SPARK_MASTER_URL}" &

# Launch History Node
sh -c "start-history-server.sh" &

echo "Spark Cluster Up"
wait
