#!/usr/bin/env bash
set -o errexit

echo "Updating permissions for debezium connector..."
./bin/mysql -uroot -pmagento << EOF
USE mysql;
GRANT SELECT, PROCESS, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'magento'@'%';
GRANT LOCK TABLES ON magento.* TO 'magento'@'%';
FLUSH PRIVILEGES;
EOF
