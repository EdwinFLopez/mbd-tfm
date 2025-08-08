#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Configuring MongoDB sink connector..."
curl -X POST http://localhost:8083/connectors -H 'Content-Type: application/json' -d @- << EOF
{
  "name": "mongodb-sink",
  "config": {
      "connector.class": "io.debezium.connector.mongodb.MongoDbSinkConnector",
      "mongodb.connection.string": "mongodb://mongodb-atlas:27017",
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
      "mongo.errors.log.enable": "true",
      "errors.log.include.messages": "true",
      "document.id.strategy": "com.mongodb.kafka.connect.sink.processor.id.strategy.BsonOidStrategy",
      "post.processor.chain": "com.mongodb.kafka.connect.sink.processor.DocumentIdAdder",
      "delete.on.null.values": "false",
      "writemodel.strategy": "com.mongodb.kafka.connect.sink.writemodel.strategy.UpdateOneBusinessKeyTimestampStrategy",
      "change.data.capture.handler": "com.mongodb.kafka.connect.sink.cdc.debezium.rdbms.mysql.MysqlHandler"
  }
}
EOF
