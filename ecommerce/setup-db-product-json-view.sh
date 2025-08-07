#!/usr/bin/env bash
set -o errexit

echo "######################################################################"
echo "Defining MysqlDb View: Products_With_Attrs_Json_View..."

bin/mysql -umagento -pmagento << EOF
USE magento;

create or replace view products_with_attrs_json_view as
with cte_product_entity as (

    select
        entity_type_id as product_type_id,
        entity_type_code
    from eav_entity_type
    where entity_type_code = 'catalog_product'
    limit 1

), cte_attribute_sets as (

    select
        attribute_set_id,
        attribute_set_name
    from eav_attribute_set at
    where exists (
        select 1
        from cte_product_entity
        where product_type_id = at.entity_type_id
        limit 1
    )

), cte_product_attributes as (

    select
        pas.attribute_set_id,
        pas.attribute_set_name,
        eea.attribute_id,
        eat.attribute_code,
        eat.backend_type,
        eat.default_value,
        eat.frontend_input as attribute_input,
        eat.frontend_label as attribute_label,
        eat.note as attribute_note,
        cea.is_global,
        cea.is_visible,
        cea.is_searchable,
        cea.is_filterable,
        cea.apply_to,
        cea.additional_data
    from cte_attribute_sets pas
    join eav_entity_attribute eea
      on pas.attribute_set_id = eea.attribute_set_id
    join eav_attribute eat
      on eat.attribute_id = eea.attribute_id
    join catalog_eav_attribute cea
      on eat.attribute_id = cea.attribute_id
    where exists (
        select 1
        from cte_product_entity pe
        where eat.entity_type_id = pe.product_type_id
    )

), cte_product_ratings as (

    select
        rv.entity_pk_value as product_id,
        sum(rv.percent) / count(1) as rating_pct,
        sum(rv.value) / count(1)   as rating_val
    from rating_option_vote rv
    group by rv.entity_pk_value

), cte_products_categories as (

    with cte_category_entity as (

        select
            entity_type_id as category_type_id,
            entity_type_code
        from eav_entity_type
        where entity_type_code = 'catalog_category'
        limit 1

    )
    select
        cxp.product_id,
        json_arrayagg(cat.value) as prd_categories
    from catalog_category_product cxp
    join catalog_category_entity_varchar cat
      on cat.entity_id = cxp.category_id
    where cat.attribute_id = (
        select attribute_id
        from eav_attribute ea
        where ea.attribute_code = 'name'
        and exists (
            select 1
            from cte_category_entity et
            where et.category_type_id = ea.entity_type_id
            limit 1
        )
        limit 1
    )
    group by cxp.product_id

), cte_product_entity_multiselect as (

    with recursive cte_expanded_multiselect_attributes as (

        with cte_multiselect_attributes as (

            select txt.entity_id, txt.attribute_id, txt.value
            from catalog_product_entity_text txt
            where txt.value is not null
            and txt.value <> ''
            and exists (
                select 1
                from eav_attribute eav
                where eav.attribute_id = txt.attribute_id
                and eav.backend_type = 'text'
                and eav.frontend_input = 'multiselect'
            )
        )
        select
            msa.entity_id,
            msa.attribute_id,
            msa.value as attribute_values,
            if(
                instr(msa.value,',')>0, substring_index(msa.value, ',', 1), msa.value
            ) as option_id,
            if(
                instr(msa.value,',')>0, substr(msa.value, length(substring_index(msa.value,',',1)) + 2), ''
            ) as rest_options
        from cte_multiselect_attributes msa

        union all

        select
            ms.entity_id,
            ms.attribute_id,
            ms.attribute_values,
            substring_index(ms.rest_options, ',', 1) as option_id,
            substr(ms.rest_options, length(substring_index(ms.rest_options, ',', 1)) + 2)
        from cte_expanded_multiselect_attributes ms
        where ms.rest_options <> ''

    ), cte_multiselect_options as (

        select
            opt.attribute_id,
            opt.option_id,
            ovl.value as option_value
        from eav_attribute_option opt
        join eav_attribute_option_value ovl
          on opt.option_id = ovl.option_id
        where ovl.store_id = 0
          and exists (
            select 1
            from eav_attribute attr
            join cte_product_entity pe
              on attr.entity_type_id = pe.product_type_id
            where attr.attribute_id = opt.attribute_id
            and attr.frontend_input='multiselect'
        )

    ), cte_selected_multiselect_attributes as (

        select
            cpt.entity_id,
            cpt.attribute_id,
            cpt.value,
            msp.option_value,
            msa.attribute_values,
            msa.option_id,
            msa.rest_options
        from cte_expanded_multiselect_attributes msa
        left join cte_multiselect_options msp
            on msa.attribute_id=msp.attribute_id
            and msa.option_id = msp.option_id
        right join catalog_product_entity_text cpt
            on cpt.entity_id = msa.entity_id
            and cpt.attribute_id = msa.attribute_id
        where cpt.store_id = 0

    )
    select
        sma.entity_id,
        sma.attribute_id,
        json_arrayagg(
            if(sma.option_id is null, sma.value, sma.option_value)
        ) as txt_values
    from cte_selected_multiselect_attributes sma
    group by sma.entity_id, sma.attribute_id

), cte_product_attr_values as (

    select entity_id, attribute_id, txt_values as attr_value
    from cte_product_entity_multiselect
    where txt_values is not null
    and txt_values <> json_array(null)

    union all

    select entity_id, attribute_id, json_array(value) as attr_value
    from catalog_product_entity_varchar
    where value is not null
    and store_id = 0

    union all

    select entity_id, attribute_id, json_array(value) as attr_value
    from catalog_product_entity_datetime
    where value is not null
    and store_id = 0

    union all

    select entity_id, attribute_id, json_array(value) as attr_value
    from catalog_product_entity_decimal
    where value is not null
    and store_id = 0

    union all

    select entity_id, attribute_id, json_array(value) as attr_value
    from catalog_product_entity_int
    where value is not null
    and store_id = 0

), cte_products_with_attrs_view as (

    select
        entity_id as product_id,
        json_objectagg(
            attribute_code,
            json_object(
                'backend_type', pwa.backend_type,
                'attribute_input', pwa.attribute_input,
                'attribute_label', pwa.attribute_label,
                'is_visible', pwa.is_visible,
                'is_searchable', pwa.is_searchable,
                'is_filterable', pwa.is_filterable,
                'apply_to', pwa.apply_to,
                'additional_data', pwa.additional_data,
                'attribute_note', pwa.attribute_note,
                'default_value', pwa.default_value,
                'value', if (
                    json_length(attr_value)>1, attr_value, json_extract(attr_value, '\$[0]')
                )
            )
        ) as prod_attr_values
    from cte_product_attr_values cpv
    join cte_product_attributes pwa using(attribute_id)
    group by entity_id

)
select
    prd.entity_id as product_id,
    prd.sku as product_sku,
    cast(json_unquote(json_extract(att.prod_attr_values, '\$.name.value')) as char(64)) as product_name,
    json_object(
        'product_sku', prd.sku,
        'product_type', prd.type_id,
        'product_categories', cat.prd_categories,
        'product_attribute_set', ast.attribute_set_name,
        'product_ratings', coalesce(rnk.rating_val, 0),
        'product_ratings_pct', coalesce(rnk.rating_pct, 0),
        'product_attributes', att.prod_attr_values
    ) as product_properties,
    prd.created_at as product_created_at,
    prd.updated_at as product_updated_at
from catalog_product_entity prd
join cte_attribute_sets ast
  using (attribute_set_id)
left join cte_product_ratings rnk
   on prd.entity_id = rnk.product_id
left join cte_products_categories cat
   on prd.entity_id = cat.product_id
left join cte_products_with_attrs_view att
   on prd.entity_id = att.product_id
;
EOF

echo "MysqlDb View has been correctly defined..."
echo "######################################################################"
echo ""
