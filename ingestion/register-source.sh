#!/usr/bin/env bash
set -o errexit

echo "Creating MySQL source connector..."
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @- << EOF
{
  "name": "mysql-source",
  "config": {
      "connector.class": "io.debezium.connector.mysql.MySqlConnector",
      "tasks.max": "1",
      "database.hostname": "mysql",
      "database.port": "3306",
      "database.user": "mysqluser",
      "database.password": "mysqlpw",
      "database.server.id": "184054",
      "database.server.name": "mysql_server",
      "database.whitelist": "testdb",
      "table.whitelist": "testdb.your_table_name",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "key.converter.schemas.enable": "false",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter.schemas.enable": "false"
  }
}
EOF
