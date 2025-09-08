from urllib.parse import quote

import requests
import streamlit as st
import pandas as pd

__STATUS_PIPELINE_RUNNING__ = "embeddings_pipeline_running"

from streamlit.elements.lib.column_types import ColumnConfig

from commons.constants import WEBAPI_URL


def render_ui() -> None:
    """
    Renders the main UI.
    """
    st.set_page_config(
        page_title="Product Recommendations for Magento eCommerce",
        layout="wide"
    )

    # Initial state (could also be persisted in session_state)
    if __STATUS_PIPELINE_RUNNING__ not in st.session_state:
        st.session_state[__STATUS_PIPELINE_RUNNING__] = False

    landing_page = st.Page(
        _ui_page_welcome,
        title="Product Recommendations for Magento eCommerce > Home",
        icon=":material/home:",
        url_path="/home",
        default=True
    )
    recommendations_page = st.Page(
        _ui_page_recommendations,
        title="Recommendations",
        icon=":material/editor_choice:",
        url_path = "/recommendations"
    )
    embeddings_page = st.Page(
        _ui_page_calculate_embeddings,
        title="Calculate Embeddings Job",
        icon=":material/function:",
        url_path = "/embeddings"
    )

    st.navigation(
        [landing_page, embeddings_page, recommendations_page],
        expanded=True
    ).run()


def _ui_page_welcome() -> None:
    st.header("Product Recommendations")
    st.subheader("for Magento eCommerce")
    st.markdown("---")


def _ui_page_recommendations() -> None:
    """
    Renders the recommendations page.
    """
    def _config_search_dataframe_columns() -> dict[str, ColumnConfig]:
        return {
            "product_sku": st.column_config.TextColumn(
                label="SKU", max_chars=64, width="medium", pinned=True
            ),
            "product_name": st.column_config.TextColumn(
                label="Product Name", max_chars=100, width="large"
            ),
            "product_properties": st.column_config.JsonColumn(
                label="JSON Properties", help="Product Properties as JSON", width="large"
            ),
            "product_flat_props": st.column_config.TextColumn(
                label="Flat Properties", help="Product Properties as Flat Text", max_chars=1000, width="large"
            ),
            "product_embeddings": st.column_config.ListColumn(
                label="Vector Embeddings", help="Product Vector Embeddings", width="medium"
            ),
            "product_created_at": st.column_config.DatetimeColumn(
                label="Created", help="Product Creation Date", width="small", format="calendar"
            ),
            "product_updated_at": st.column_config.DatetimeColumn(
                label="Last Updated", help="Product Last Update Date", width="small", format="calendar"
            ),
            "product_deleted_at": st.column_config.DatetimeColumn(
                label="Deleted At", help="Date in which the product was deleted from ecommerce", width="small", format="calendar"
            ),
            "embeddings_updated_at": st.column_config.DatetimeColumn(
                label="Embeddings Updated At", help="Date in which the embeddings for the product were updated for the last time"
            )
        }

    def _config_recommendations_dataframe_columns() -> dict[str, ColumnConfig]:
        col_config = _config_search_dataframe_columns().copy()
        col_config["similarity_score"] = st.column_config.NumberColumn(
            label="Similarity Score", width="medium", min_value=-1.0, max_value=1.0, format="plain", pinned=True
        )
        return col_config


    # Query search section ------------------------------------ *
    st.subheader("Search Products")
    query: str = quote(st.text_input("Enter search term:"))
    has_search_data = False
    search_columns_config = _config_search_dataframe_columns()
    filtered_data_df = {}
    if query and not query.strip().isspace():
        response = requests.get(f"{WEBAPI_URL}/data/search/{query}")
        if response.ok:
            data = response.json()
            has_search_data = len(data) if data and len(data) > 0 else False
            filtered_data_df = pd.DataFrame(data if has_search_data else {})
            if has_search_data:
                st.info(f"{len(data)} record{'' if len(data) == 1 else 's'} found for {query}.")
            else:
                st.warning(f"No results found for {query}.")
        else:
            st.error(f"Error fetching {query}: {response.text}")

    event = st.dataframe(
        data=filtered_data_df,
        column_config=search_columns_config,
        on_select="rerun",
        selection_mode="single-row",
        width='stretch',
        hide_index=True,
        column_order=search_columns_config.keys()
    )
    st.markdown("---")

    recommendations_df = {}
    if has_search_data and event.selection.rows:
        sku_df = filtered_data_df.iloc[event.selection.rows]
        sku = sku_df['product_sku'].values[0]
        response = requests.get(f"{WEBAPI_URL}/data/recommendations/{sku}")
        if response.ok:
            data = response.json()
            has_recommendations = len(data) if data and len(data) > 0 else False
            recommendations_df = pd.DataFrame(data if has_recommendations else {})
            if has_recommendations:
                st.info(f"Selected SKU {sku}: {len(data)} recommendation{'' if len(data) == 1 else 's'} found for {sku}.")
            else:
                st.warning(f"No recommendations found for {sku}.")
        else:
            st.error(f"Error fetching recommendations for {sku}: {response.text}")

    # Recommendations query section ------------------------------------------ *
    recommendations_columns_config = _config_recommendations_dataframe_columns()
    st.subheader("Recommendations")
    st.dataframe(
        data=recommendations_df,
        column_config=recommendations_columns_config,
        on_select="rerun",
        selection_mode="single-row",
        width='stretch',
        hide_index=True,
        column_order=recommendations_columns_config.keys()
    )


def _ui_page_calculate_embeddings() -> None:
    st.subheader("Calculate embeddings")
    if __STATUS_PIPELINE_RUNNING__ not in st.session_state or not st.session_state[__STATUS_PIPELINE_RUNNING__]:
        btn_label = "🔴 Start Embeddings Creation Process"
    else:
        btn_label = "🟢 Stop Processing Embeddings......."

    st.button(
        label=btn_label,
        type=f"{'primary' if not st.session_state[__STATUS_PIPELINE_RUNNING__] else 'secondary'}",
        icon=":material/engineering:",
        on_click=__on_start_embeddings_calculation_callback,
        width=500,
    )
    st.markdown("🟢 Running" if st.session_state[__STATUS_PIPELINE_RUNNING__] else "🔴 Stopped")
    st.markdown("---")

    response = requests.get(f"{WEBAPI_URL}/embeddings/status/jobs")
    if response.ok:
        data = response.json()
    else:
        data = {}
        st.error(f"Error fetching status for embeddings jobs: {response.text}")

    columns_config = {
        "job_id": st.column_config.TextColumn(label="Job Id", width="large"),
        "job_status": st.column_config.TextColumn(label="Job Status", width="medium"),
        "job_last_error": st.column_config.TextColumn(label="Last Error", width="large")
    }
    st.dataframe(
        data=data,
        hide_index=True,
        width='stretch',
        column_config=columns_config,
        column_order=columns_config.keys(),
    )


def __on_start_embeddings_calculation_callback() -> None:
    is_running = st.session_state[__STATUS_PIPELINE_RUNNING__]
    if is_running:
        return

    response = requests.post(f"{WEBAPI_URL}/embeddings/start")
    if not response.ok:
        st.session_state[__STATUS_PIPELINE_RUNNING__] = True
        st.error(f"Error starting embeddings job: {response.text}")
        return

    # {
    #   "job_id": "913fc681-2d98-4ac6-bcc4-4eb5d2b882f2",
    #   "job_status": "running" | "completed" | "failed",
    #   "job_last_error": null | str
    # }
    is_complete = False
    data = response.json()
    if data and data['job_status'] == 'running':
        st.info(f"Embeddings job {data['job_id']} is still running.")
    elif data and data['job_status'] == 'completed':
        is_complete = True
        st.info(f"Embeddings job {data['job_id']} is complete.")
    elif data and data['job_status'] == 'failed':
        is_complete = True
        st.warning(f"Embeddings job {data['job_id']} failed due {data['job_last_error']}.")
    else:
        st.error(f"Embeddings job didn't return a status..")
    st.session_state[__STATUS_PIPELINE_RUNNING__] = is_complete
