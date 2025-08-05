#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Creating materialized view tables"
./bin/mysql -uroot -pmagento << EOF
USE magento;

EOF
echo "######################################################################"
echo "Materialized view tables have been setup correctly...."
echo ""
