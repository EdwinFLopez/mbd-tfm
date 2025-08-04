with category_entity as (

    select
        entity_type_id as category_type_id,
        entity_type_code
    from eav_entity_type
    where entity_type_code = 'catalog_category'
    limit 1

), product_entity as (

    select
        entity_type_id as product_type_id,
        entity_type_code
    from eav_entity_type
    where entity_type_code = 'catalog_product'
    limit 1

), attribute_sets as (

    select
        attribute_set_id,
        attribute_set_name
    from eav_attribute_set at
    where exists (
        select 1
        from product_entity
        where product_type_id = at.entity_type_id
        limit 1
    )

), product_attributes as (

    select
        cpe.entity_id as product_id,
        cpe.sku,
        cpe.type_id,
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
    from eav_entity_attribute eea
    join eav_attribute eat
      on eat.attribute_id = eea.attribute_id
    join catalog_eav_attribute cea
      on eat.attribute_id = cea.attribute_id
    join catalog_product_entity cpe
      on cpe.attribute_set_id = eea.attribute_set_id
    join attribute_sets pas
      on cpe.attribute_set_id = pas.attribute_set_id
    where eat.is_user_defined = 1
      and exists (
        select 1
        from product_entity pe
        where eat.entity_type_id = pe.product_type_id
    ) and (
        select 1
        from attribute_sets pas
        where eea.attribute_set_id = pas.attribute_set_id
    )

), product_ratings as (

    select rv.entity_pk_value as product_id,
           sum(rv.percent) / count(1) as rating_pct,
           sum(rv.value) / count(1)   as rating_val
    from rating_option_vote rv
    group by rv.entity_pk_value

), products_categories as (

    select cxp.product_id, json_arrayagg(cat.value) as prd_categories
    from catalog_category_product cxp
    left join catalog_category_entity_varchar cat
        on  cat.entity_id = cxp.category_id
        and cat.attribute_id = (
           select attribute_id
           from eav_attribute ea
           where ea.attribute_code = 'name'
             and exists (
               select 1
               from category_entity et
               where et.category_type_id = ea.entity_type_id
               limit 1
            )
       )
    group by cxp.product_id

), catalog_product_entity_multiselect as (

    with recursive expanded_multiselect_attributes as (

        with multiselect_attributes as (

            select txt.entity_id, txt.attribute_id, txt.value
            from catalog_product_entity_text txt
            where exists (
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
            if (instr(msa.value,',')>0,
                substring_index(msa.value, ',', 1),
                msa.value
            ) as option_id,
            IF(instr(msa.value,',')>0,
               substr(msa.value, length(substring_index(msa.value,',',1)) + 2),
               ''
            ) as rest_options
        from multiselect_attributes msa
        where msa.value is not null and msa.value != ''

        union all

        select
            ms.entity_id,
            ms.attribute_id,
            ms.attribute_values,
            substring_index(ms.rest_options, ',', 1) as option_id,
            substr(ms.rest_options, length(substring_index(ms.rest_options, ',', 1)) + 2)
        from expanded_multiselect_attributes ms
        where ms.rest_options != ''

    ), multiselect_options as (

        select distinct
            attr.attribute_id,
            opt.option_id,
            case
                when ovl.value is null and osw.value is null
                    then null
                when ovl.value = osw.value
                    then ovl.value
                when ovl.value is not null and osw.value is not null
                    then concat(ovl.value, '(', osw.value, ')')
                else coalesce(ovl.value, osw.value)
                end as option_value
        from eav_attribute attr
                 join eav_attribute_option opt
                      on attr.attribute_id = opt.attribute_id
                 left join eav_attribute_option_value ovl
                           on opt.option_id = ovl.option_id
                 left join eav_attribute_option_swatch osw
                           on opt.option_id = osw.option_id
        where attr.frontend_input like 'multiselect'
          and exists (
            select 1
            from product_entity et
            where et.product_type_id = attr.entity_type_id
        )

    ), selected_multiselect_attributes as (

        select
            cpt.entity_id,
            cpt.attribute_id,
            cpt.store_id,
            cpt.value,
            msa.attribute_values,
            msa.option_id,
            msp.option_value,
            msa.rest_options
        from expanded_multiselect_attributes msa
        left join multiselect_options msp
           on msa.attribute_id=msp.attribute_id
           and msa.option_id = msp.option_id
        right join catalog_product_entity_text cpt
            on cpt.entity_id = msa.entity_id
            and cpt.attribute_id = msa.attribute_id

    )
    select
        sma.entity_id,
        sma.store_id,
        sma.attribute_id,
        json_arrayagg(
                if(sma.option_id is null, sma.value, sma.option_value)
        ) as txt_values
    from selected_multiselect_attributes sma
    group by sma.entity_id, sma.store_id, sma.attribute_id

), product_catalog_view as (

    select pwa.product_id,
           pwa.sku,
           pwa.type_id,
           pwa.attribute_set_id,
           pwa.attribute_set_name,
           pwa.attribute_id,
           pwa.attribute_code,
           pwa.backend_type,
           pwa.attribute_input,
           pwa.attribute_label,
           pwa.is_visible,
           pwa.is_searchable,
           pwa.is_filterable,
           pwa.apply_to,
           pwa.additional_data,
           pwa.attribute_note,
           pwa.default_value,
           txt.store_id,
           txt.txt_values as vtx_value,
           var.store_id as var_store_id,
           var.value as var_value,
           vdt.store_id as vdt_store_id,
           vdt.value as vdt_value,
           vdc.store_id as vdc_store,
           vdc.value as vdc_value,
           vin.store_id as vin_store_id,
           vin.value as vin_value
    from product_attributes pwa
    left join catalog_product_entity_multiselect txt
           on  pwa.product_id = txt.entity_id
           and pwa.attribute_id = txt.attribute_id
    left join catalog_product_entity_varchar var
           on  pwa.product_id = var.entity_id
           and pwa.attribute_id = var.attribute_id
    left join catalog_product_entity_datetime vdt
           on  pwa.product_id = vdt.entity_id
           and pwa.attribute_id = vdt.attribute_id
    left join catalog_product_entity_decimal vdc
           on  pwa.product_id = vdc.entity_id
           and pwa.attribute_id = vdc.attribute_id
    left join catalog_product_entity_int vin
           on  pwa.product_id = vin.entity_id
           and pwa.attribute_id = vin.attribute_id
    where pwa.sku like '24-MB06%'

), final_query as (

    select pcv.sku,
           pcv.type_id,
           pcv.attribute_set_name,
           JSON_OBJECTAGG(
                pcv.attribute_code,
                case backend_type
                   when "varchar" then json_array(pcv.var_value)
                   when "decimal" then json_array(pcv.vdc_value)
                   when "int" then json_array(pcv.vin_value)
                   when "text" then pcv.vtx_value
                   when "datetime" then json_array(pcv.vdt_value)
                   else json_array(pcv.default_value)
                end
           ) as product_attributes
    From product_catalog_view pcv
    group by pcv.sku, pcv.type_id, pcv.attribute_set_name

)
select * from final_query
;

with recursive expanded_multiselect_attributes as (
    with multiselect_attributes as (
        select txt.entity_id, txt.attribute_id, txt.value
        from catalog_product_entity_text txt
        where exists (
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
        if (instr(msa.value,',')>0,
            substring_index(msa.value, ',', 1),
            msa.value
        ) as option_id,
        IF(instr(msa.value,',')>0,
           substr(msa.value, length(substring_index(msa.value,',',1)) + 2),
           ''
        ) as rest_options
    from multiselect_attributes msa
    where msa.value is not null and msa.value != ''

    union all

    select
        ms.entity_id,
        ms.attribute_id,
        ms.attribute_values,
        substring_index(ms.rest_options, ',', 1) as option_id,
        substr(ms.rest_options, length(substring_index(ms.rest_options, ',', 1)) + 2)
    from expanded_multiselect_attributes ms
    where ms.rest_options != ''
), product_entity as (
    select
        entity_type_id as product_type_id,
        entity_type_code
    from eav_entity_type
    where entity_type_code = 'catalog_product'
    limit 1
), multiselect_options as (
    select distinct
        attr.attribute_id,
        opt.option_id,
        case
            when ovl.value is null and osw.value is null
                then null
            when ovl.value = osw.value
                then ovl.value
            when ovl.value is not null and osw.value is not null
                then concat(ovl.value, '(', osw.value, ')')
            else coalesce(ovl.value, osw.value)
            end as option_value
    from eav_attribute attr
             join eav_attribute_option opt
                  on attr.attribute_id = opt.attribute_id
             left join eav_attribute_option_value ovl
                       on opt.option_id = ovl.option_id
             left join eav_attribute_option_swatch osw
                       on opt.option_id = osw.option_id
    where attr.frontend_input like 'multiselect'
      and exists (
        select 1
        from product_entity et
        where et.product_type_id = attr.entity_type_id
    )
), selected_multiselect_attributes as (
    select
        cpt.entity_id,
        cpt.attribute_id,
        cpt.value,
        msa.attribute_values,
        msa.option_id,
        msp.option_value,
        msa.rest_options
    from expanded_multiselect_attributes msa
             left join multiselect_options msp
                       on  msa.attribute_id=msp.attribute_id
                           and msa.option_id = msp.option_id
             right join catalog_product_entity_text cpt
                        on cpt.entity_id = msa.entity_id
                            and cpt.attribute_id = msa.attribute_id
)
select
    sma.entity_id,
    sma.attribute_id,
    json_arrayagg(
        if(sma.option_id is null, sma.value, sma.option_value)
    ) as txt_values
from selected_multiselect_attributes sma
group by sma.entity_id, sma.attribute_id
;