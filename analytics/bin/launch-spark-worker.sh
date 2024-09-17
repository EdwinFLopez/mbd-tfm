#!/usr/bin/bash
set -eo pipefail

sh -c "$SPARK_HOME/sbin/start-worker.sh spark://$SPARK_MASTER_HOST:$SPARK_MASTER_PORT"
