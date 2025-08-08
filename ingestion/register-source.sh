#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Configuring MySQL source connector..."
curl -s -X DELETE http://localhost:8083/connectors/mysql-source > /dev/null
curl -X POST http://localhost:8083/connectors -H 'Content-Type: application/json' -d @- << EOF
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
      "table.whitelist": "magento.catalog_category_entity_varchar,magento.catalog_category_product,magento.catalog_eav_attribute,magento.catalog_product_entity,magento.catalog_product_entity_datetime,magento.catalog_product_entity_decimal,magento.catalog_product_entity_int,magento.catalog_product_entity_text,magento.catalog_product_entity_varchar,magento.eav_attribute,magento.eav_attribute_option,magento.eav_attribute_option_value,magento.eav_attribute_set,magento.eav_entity_attribute,magento.eav_entity_type,magento.rating_option_vote",
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
