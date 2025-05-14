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
             join product_attributeset pas
                  on cpe.attribute_set_id = pas.attribute_set_id
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
)
select *
from catalog_products;




select eea.attribute_set_id, eea.attribute_id,
       eat.backend_type,
       eat.default_value,
       eat.attribute_code,
       eat.frontend_label as attribute_label,
       cea.*
from eav_entity_attribute eea
join eav_attribute eat
    on eea.attribute_id = eat.attribute_id
        and eat.entity_type_id = 4
        and eea.attribute_set_id = 15
join magento.catalog_eav_attribute cea
    on eat.attribute_id = cea.attribute_id
-- where
-- cea.is_global = 1 and
-- cea.is_visible = 1
-- or
-- cea.is_visible_on_front = 1
-- or
-- cea.is_searchable = 1
-- or
-- cea.is_filterable_in_search = 1
-- or
-- cea.is_visible_in_advanced_search = 1
-- or
-- cea.is_filterable_in_grid = 1
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
