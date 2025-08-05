#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Updating ecommerce mysql permissions for using debezium connector....."
./bin/mysql -uroot -pmagento << EOF
USE mysql;
GRANT SELECT, PROCESS, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'magento'@'%';
GRANT LOCK TABLES ON magento.* TO 'magento'@'%';
FLUSH PRIVILEGES;
EOF
echo "######################################################################"
echo "Permissions for using debezium connector have been setup correctly...."
echo ""
