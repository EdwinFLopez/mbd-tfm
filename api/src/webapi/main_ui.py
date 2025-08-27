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
    if "embeddings_pipeline_running" not in st.session_state:
        st.session_state.is_running = False

    # Fake product data for demo purposes
    data = pd.DataFrame({
        "product_sku": ["SKU001", "SKU002", "SKU003"],
        "product_name": ["Red Shoes", "Blue Hat", "Green Shirt"]
    })
    st.session_state.is_running = __render_left_side(st.session_state.is_running)
    __render_right_side(data)


def __render_left_side(is_running: bool) -> bool:
    """
    Render the left side UI: pipeline status and start/stop button.
    Returns the updated pipeline status.
    """
    with st.sidebar:
        st.title("Product Recommendations")
        st.subheader(f"for Magento eCommerce")
        st.markdown("---")
        st.markdown(f"**Embeddings creation process**")
        st.markdown("🟢 Running" if is_running else "🔴 Stopped")
        if st.button("Start Embeddings Creation" if not is_running else "Stop Embeddings Creation"):
            st.session_state[__STATUS_PIPELINE_RUNNING__] = not is_running
        st.markdown("---")
    return is_running


def __render_right_side(data: pd.DataFrame) -> None:
    """
    Render the right side UI: search box and results table.
    """
    st.subheader("Search Products")
    filtered = data
    query: str = st.text_input("Enter search term:")
    if query:
        filtered = data[data["product_name"].str.contains(query, case=False, na=False)]
    st.dataframe(filtered)
    st.markdown("---")

    st.subheader("Recommendations")
    st.dataframe()
