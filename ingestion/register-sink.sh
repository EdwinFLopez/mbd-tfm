#!/usr/bin/env bash

echo 'Creating MongoDB sink connector...' 
curl -X POST http://localhost:8083/connectors -H 'Content-Type: application/json' -d @- << EOF
{
  "name": "mongodb-sink",
  "config": {
      "connector.class": "com.mongodb.kafka.connect.MongoSinkConnector",
      "tasks.max": "1",
      "topics": "mysql_server.testdb.your_table_name",
      "connection.uri": "mongodb://mongodb:27017",
      "database": "your_mongodb_db",
      "collection": "your_collection_name",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "key.converter.schemas.enable": "false",
      "value.converter.schemas.enable": "false"
  }
}
EOF
