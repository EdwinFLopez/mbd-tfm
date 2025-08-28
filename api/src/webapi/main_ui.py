import streamlit as st
import pandas as pd

__STATUS_PIPELINE_RUNNING__ = "embeddings_pipeline_running"

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
        __ui_page_welcome__,
        title="Product Recommendations for Magento eCommerce > Home",
        icon=":material/home:",
        default=True
    )
    recommendations_page = st.Page(
        __ui_page_recommendations__,
        title="Recommendations",
        icon=":material/editor_choice:"
    )
    embeddings_page = st.Page(
        __ui_page_calculate_embeddings__,
        title="Calculate Embeddings",
        icon=":material/function:"
    )

    st.navigation(
        [landing_page, embeddings_page, recommendations_page],
        expanded=True
    ).run()


def __ui_page_welcome__() -> None:
    st.header("Product Recommendations")
    st.subheader("for Magento eCommerce")
    st.markdown("---")


def __ui_page_recommendations__() -> None:
    # Fake product data for demo purposes
    data = pd.DataFrame({
        "product_sku": ["SKU001", "SKU002", "SKU003"],
        "product_name": ["Red Shoes", "Blue Hat", "Green Shirt"]
    })
    st.subheader("Search Products")
    filtered = data
    query: str = st.text_input("Enter search term:")
    if query:
        filtered = data[data["product_name"].str.contains(query, case=False, na=False)]
    st.dataframe(filtered)
    st.markdown("---")

    st.subheader("Recommendations")
    st.dataframe()

def __ui_page_calculate_embeddings__() -> None:
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
    st.dataframe()


def __on_start_embeddings_calculation_callback() -> None:
    st.session_state[__STATUS_PIPELINE_RUNNING__] = not st.session_state[__STATUS_PIPELINE_RUNNING__]