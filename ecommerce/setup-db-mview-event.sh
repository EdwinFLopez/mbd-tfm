#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Creating materialized view support event..."

bin/mysql -umagento -pmagento << EOF
USE magento;

drop event if exists refresh_catalog_products_mview
;

create event refresh_catalog_products_mview
on schedule every 5 minute
starts current_timestamp
ends current_timestamp + interval 10 month
on completion preserve
enable
do
  call refresh_catalog_products_mview_sp()
;
EOF

echo "Materialized view support event has been setup correctly..."
echo "######################################################################"
echo ""
