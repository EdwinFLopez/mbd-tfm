#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Creating materialized view support procedure..."

bin/mysql -umagento -pmagento << EOF
USE magento;

drop procedure if exists refresh_catalog_products_mview_sp
;

delimiter @@
create procedure refresh_catalog_products_mview_sp()
begin
      -- 1. Create temporary table to materialize a query.
      drop temporary table if exists tmp_catalog_products_mview
      ;

      -- 2. Materialize the query into the tmporary table.
      create temporary table tmp_catalog_products_mview as
        select
            product_id,
            product_sku,
            product_name,
            product_properties,
            product_created_at,
            product_updated_at
        from products_with_attrs_json_view
      ;

      -- 3. Add pk index to tmporary table
      alter table tmp_catalog_products_mview
        add constraint tmp_catalog_products_mview_pk
        primary key (product_id)
      ;

      -- 4. Store new records and update changed fields into materialized view table
      insert into catalog_products_mview (
        product_id,
        product_sku,
        product_name,
        product_properties,
        product_created_at,
        product_updated_at
      )
      select
        tmp.product_id,
        tmp.product_sku,
        tmp.product_name,
        tmp.product_properties,
        tmp.product_created_at,
        tmp.product_updated_at
      from tmp_catalog_products_mview tmp
      on duplicate key
      update
        catalog_products_mview.product_sku = if(
            catalog_products_mview.product_sku != tmp.product_sku,
            tmp.product_sku, catalog_products_mview.product_sku
          ),
        catalog_products_mview.product_name = if(
            catalog_products_mview.product_name != tmp.product_name,
            tmp.product_name, catalog_products_mview.product_name
          ),
        catalog_products_mview.product_properties = if(
            catalog_products_mview.product_properties != tmp.product_properties,
            tmp.product_properties, catalog_products_mview.product_properties
          ),
        catalog_products_mview.product_created_at = if(
            catalog_products_mview.product_created_at != tmp.product_created_at,
            tmp.product_created_at, catalog_products_mview.product_created_at
          ),
        catalog_products_mview.product_updated_at = if(
            catalog_products_mview.product_updated_at != tmp.product_updated_at,
            tmp.product_updated_at, catalog_products_mview.product_updated_at
          ),
        catalog_products_mview.product_deleted_at = if(
            product_deleted_at is not null,
            product_deleted_at, null
          )
      ;

      -- 5. Mark removed records by setting product_deleted_at with current timestamp.
      update catalog_products_mview
        set product_deleted_at = now()
      where product_id not in (
        select product_id
        from tmp_catalog_products_mview
      )
      and product_deleted_at is null
      ;
end
@@
delimiter ;
EOF

echo "REFRESH_CATALOG_PRODUCTS_MVIEW_SP support procedure has been setup correctly..."
echo "######################################################################"
echo ""
