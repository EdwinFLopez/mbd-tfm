#!/usr/bin/bash
set -eo pipefail

sh -c '"$SPARK_HOME/sbin/start-history-server.sh"'
