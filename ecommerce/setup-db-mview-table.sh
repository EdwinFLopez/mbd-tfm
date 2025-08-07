#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Creating materialized view support table: CATALOG_PRODUCTS_MVIEW ..."

bin/mysql -umagento -pmagento << EOF
USE magento;

drop table if exists catalog_products_mview
;

create table if not exists catalog_products_mview as
  select
      product_id,
      product_sku,
      product_name,
      product_properties,
      product_created_at,
      product_updated_at,
      cast(null as datetime) as product_deleted_at
  from products_with_attrs_json_view
  limit 0
;

alter table catalog_products_mview
  add constraint catalog_products_mview_pk
  primary key (product_id)
;

alter table catalog_products_mview
  add index catalog_products_mview_idx_product_sku (product_sku)
;

alter table catalog_products_mview
  add index catalog_products_mview_idx_product_name (product_name)
;
EOF

echo "Materialized view support table has been setup correctly..."
echo "######################################################################"
echo ""
