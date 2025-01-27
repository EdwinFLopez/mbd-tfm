#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Configuring MongoDB sink connector..."
curl -X POST http://localhost:8083/connectors -H 'Content-Type: application/json' -d @- << EOF
{
  "name": "mongodb-sink",
  "config": {
      "connector.class": "io.debezium.connector.mongodb.MongoDbSinkConnector",
      "mongodb.connection.string": "mongodb://mongodb-atlas:27017/mbdtfmdb",
      "tasks.max": "1",
      "topics.regex": "mbdtfm.magento.*",
      "sink.database": "mbdtfmdb",
      "collection": "*",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "key.converter.schemas.enable": "false",
      "value.converter.schemas.enable": "false",
      "max.num.retries": 5,
      "errors.tolerance": "all",
      "mongo.errors.tolerance": "all",
      "mongo.errors.log.enable": true,
      "errors.log.include.messages": true,
      "writemodel.strategy": "com.mongodb.kafka.connect.sink.writemodel.strategy.InsertOneDefaultStrategy",
      "change.data.capture.handler": "com.mongodb.kafka.connect.sink.cdc.debezium.rdbms.mysql.MysqlHandler"
  }
}
EOF
