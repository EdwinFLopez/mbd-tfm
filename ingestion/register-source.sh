#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Creating MySQL source connector..."
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @- << EOF
{
  "name": "mysql-source",
  "config": {
      "connector.class": "io.debezium.connector.mysql.MySqlConnector",
      "tasks.max": "1",
      "database.hostname": "host.docker.internal",
      "database.port": "3306",
      "database.user": "magento",
      "database.password": "magento",
      "database.server.id": "1",
      "database.server.name": "mysqldb",
      "database.whitelist": "magento",
      "database.include.list": "magento",
      "table.whitelist": "magento.*",
      "topic.prefix": "mbdtfm",
      "schema.history.internal.kafka.bootstrap.servers": "kafka-standalone:9092",
      "schema.history.internal.kafka.topic": "mbdtfm.schema-changes.magento",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "key.converter.schemas.enable": "false",
      "value.converter.schemas.enable": "false"
  }
}
EOF
