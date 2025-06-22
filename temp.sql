with category_entity as (
    select
        entity_type_id as category_eav_id,
        entity_type_code
    from eav_entity_type
    where entity_type_code = 'catalog_category'
    limit 1
), product_entity as (
    select
        entity_type_id as product_eav_id,
        entity_type_code
    from eav_entity_type
    where entity_type_code = 'catalog_product'
    limit 1
), product_attributeset as (
    select
        attribute_set_id,
        attribute_set_name
    from eav_attribute_set at
    where exists (
        select 1
        from product_entity
        where product_eav_id = at.entity_type_id
        limit 1
    )
), catalog_products as (
    select cpe.entity_id as catalog_product_id,
           cpe.sku,
           cpe.type_id,
           pas.attribute_set_id,
           pas.attribute_set_name
    from catalog_product_entity cpe
             join product_attributeset pas using (attribute_set_id)
), product_attributes as (
    select eea.attribute_set_id,
           eea.attribute_id,
           eat.attribute_code,
           eat.backend_type,
           eat.default_value,
           eat.frontend_label as attribute_label,
           cea.frontend_input_renderer,
           cea.is_global,
           cea.is_visible,
           cea.is_searchable,
           cea.is_filterable,
           cea.is_comparable,
           cea.is_visible_on_front,
           cea.is_html_allowed_on_front,
           cea.is_used_for_price_rules,
           cea.is_filterable_in_search,
           cea.used_in_product_listing,
           cea.used_for_sort_by,
           cea.apply_to,
           cea.is_visible_in_advanced_search,
           cea.position,
           cea.is_wysiwyg_enabled,
           cea.is_used_for_promo_rules,
           cea.is_required_in_admin_store,
           cea.is_used_in_grid,
           cea.is_visible_in_grid,
           cea.is_filterable_in_grid,
           cea.search_weight,
           cea.is_pagebuilder_enabled,
           cea.additional_data
    from eav_entity_attribute eea
             join eav_attribute eat
                  on eat.attribute_id = eea.attribute_id
             join catalog_eav_attribute cea
                  on eat.attribute_id = cea.attribute_id
    where exists (
        select 1
        from product_entity pe
        where eat.entity_type_id = pe.product_eav_id
    ) and (
        select 1
        from product_attributeset pas
        where eea.attribute_set_id = pas.attribute_set_id
    )
), products_with_attributes as (
    select prd.catalog_product_id,
           prd.sku,
           prd.type_id,
           prd.attribute_set_id,
           prd.attribute_set_name,
           attr.attribute_id,
           attr.attribute_code,
           attr.backend_type,
           attr.default_value,
           attr.attribute_label,
           attr.frontend_input_renderer,
           attr.is_global,
           attr.is_visible,
           attr.is_searchable,
           attr.is_filterable,
           attr.is_comparable,
           attr.is_visible_on_front,
           attr.is_html_allowed_on_front,
           attr.is_used_for_price_rules,
           attr.is_filterable_in_search,
           attr.used_in_product_listing,
           attr.used_for_sort_by,
           attr.apply_to,
           attr.is_visible_in_advanced_search,
           attr.position,
           attr.is_wysiwyg_enabled,
           attr.is_used_for_promo_rules,
           attr.is_required_in_admin_store,
           attr.is_used_in_grid,
           attr.is_visible_in_grid,
           attr.is_filterable_in_grid,
           attr.search_weight,
           attr.is_pagebuilder_enabled,
           attr.additional_data
    from product_attributes attr
             join catalog_products prd using (attribute_set_id)
)
select pwa.catalog_product_id,
       pwa.sku,
       pwa.type_id,
       pwa.attribute_set_id,
       pwa.attribute_set_name,
       pwa.attribute_id,
       pwa.attribute_code,
       pwa.backend_type,
       pwa.default_value,
       pwa.attribute_label,
       pwa.is_visible,
       pwa.is_searchable,
       pwa.is_filterable,
       pwa.apply_to,
       pwa.additional_data,
       txt.store_id,
       txt.value,
       var.store_id as var_store_id,
       var.value as var_value,
       vdt.store_id as vdt_store_id,
       vdt.value as vdt_value,
       vdc.store_id as vdc_store,
       vdc.value as vdc_value,
       vin.store_id as vin_store_id,
       vin.value as vin_value
from products_with_attributes pwa
         left join catalog_product_entity_text txt
                   on  pwa.catalog_product_id = txt.entity_id
                       and pwa.attribute_id = txt.attribute_id
         left join catalog_product_entity_varchar var
                   on  pwa.catalog_product_id = var.entity_id
                       and pwa.attribute_id = var.attribute_id
         left join catalog_product_entity_datetime vdt
                   on  pwa.catalog_product_id = vdt.entity_id
                       and pwa.attribute_id = vdt.attribute_id
         left join catalog_product_entity_decimal vdc
                   on  pwa.catalog_product_id = vdc.entity_id
                       and pwa.attribute_id = vdc.attribute_id
         left join catalog_product_entity_int vin
                   on  pwa.catalog_product_id = vin.entity_id
                       and pwa.attribute_id = vin.attribute_id
where pwa.sku like '24-MB06%'
-- where pwa.sku = '24-MB01'
;



SELECT t_d.attribute_id,
       e.entity_id,
       t_d.value AS default_value,
       t_s.value AS store_value,
       IF(t_s.value_id IS NULL, t_d.value, t_s.value) AS value
FROM catalog_product_entity_decimal AS t_d
         INNER JOIN catalog_product_entity AS e
                    ON e.entity_id = t_d.entity_id
         LEFT JOIN catalog_product_entity_decimal AS t_s
                   ON t_s.attribute_id = t_d.attribute_id
                       AND t_s.entity_id = t_d.entity_id
                       AND t_s.store_id = 0
WHERE (e.entity_id IN (33, 34, 35))
  AND (t_d.attribute_id IN (123, 77, 78))
  AND (t_d.store_id = IFNULL(t_s.store_id, 0))

UNION ALL
SELECT t_d.attribute_id,
       e.entity_id,
       t_d.value AS default_value,
       t_s.value AS store_value,
       IF(t_s.value_id IS NULL, t_d.value, t_s.value) AS value
FROM catalog_product_entity_varchar AS t_d
         INNER JOIN catalog_product_entity AS e
                    ON e.entity_id = t_d.entity_id
         LEFT JOIN catalog_product_entity_varchar AS t_s
                   ON t_s.attribute_id = t_d.attribute_id
                       AND t_s.entity_id = t_d.entity_id
                       AND t_s.store_id = 1
WHERE (e.entity_id IN (33, 34, 35))
  AND (t_d.attribute_id IN (73, 87))
  AND (t_d.store_id = IFNULL(t_s.store_id, 0))

UNION ALL
SELECT t_d.attribute_id,
       e.entity_id,
       t_d.value AS default_value,
       t_s.value AS store_value,
       IF(t_s.value_id IS NULL, t_d.value, t_s.value) AS value
FROM catalog_product_entity_datetime AS t_d
         INNER JOIN catalog_product_entity AS e
                    ON e.entity_id = t_d.entity_id
         LEFT JOIN catalog_product_entity_datetime AS t_s
                   ON t_s.attribute_id = t_d.attribute_id
                       AND t_s.entity_id = t_d.entity_id
                       AND t_s.store_id = 1
WHERE (e.entity_id IN (33, 34, 35))
  AND (t_d.attribute_id IN (79, 80))
  AND (t_d.store_id = IFNULL(t_s.store_id, 0))

UNION ALL
SELECT t_d.attribute_id,
       e.entity_id,
       t_d.value AS default_value,
       t_s.value AS store_value,
       IF(t_s.value_id IS NULL, t_d.value, t_s.value) AS value
FROM catalog_product_entity_int AS t_d
         INNER JOIN catalog_product_entity AS e
                    ON e.entity_id = t_d.entity_id
         LEFT JOIN catalog_product_entity_int AS t_s
                   ON t_s.attribute_id = t_d.attribute_id
                       AND t_s.entity_id = t_d.entity_id
                       AND t_s.store_id = 1
WHERE (e.entity_id IN (33, 34, 35))
  AND (t_d.attribute_id IN (136))
  -- AND (t_d.store_id = IFNULL(t_s.store_id, 0))




#wget --header="Content-Type: application/json" --post-data='{"configuredLevel": "WARN"}' http://localhost:8081/actuator/loggers/root
#wget --header="Content-Type: application/json" http://localhost:8081/actuator/loggers
