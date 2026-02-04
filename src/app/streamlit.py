import streamlit as st
import requests
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

AUTH_PASSWORD = os.environ.get("API_AUTH_PASSWORD", "")

st.set_page_config(
    page_title="Receipt Data Extraction System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)


with open(r"src/assets/streamlit.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<div class="main-title">Receipt Data Extraction System</div>',
            unsafe_allow_html=True)


# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {
        "store_name": "",
        "receipt_number": "",
        "date": "",
        "currency": "",
        "taxes": "",
        "total_amount": "",
        "items": []
    }

# Layout
col1, col2 = st.columns([0.95, 1.05], gap="large")

with col1:
    st.markdown("### Upload Receipt")

    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png'],
        help="Supported formats: JPG, JPEG, PNG"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Extract Data", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                try:
                    uploaded_file.seek(0)

                    files = {
                        "file": ("receipt.jpg", uploaded_file, "image/jpeg")}
                    headers = {
                        "X-API-Password": f"{AUTH_PASSWORD}"
                    }
                    response = requests.post(
                        "http://localhost:8000/api/v1/receipt_parser/upload",
                        files=files,
                        headers=headers,
                        timeout=30,

                    )

                    if response.status_code == 200:
                        result = response.json()
                        
                        st.session_state.extracted_data = {
                            "store_name": result.get("store_name", ""),
                            "receipt_number": result.get("receipt_number", ""),
                            "date": result.get("date", ""),
                            "currency": result.get("currency", ""),
                            "taxes": result.get("taxes", ""),
                            "total_amount": result.get("total_amount", ""),
                            "items": result.get("items", []),
                        }

                        st.rerun()
                    else:
                        st.error(
                            f"Error: Unable to process receipt (Status {response.status_code})")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Upload a receipt image to begin")

with col2:
    st.markdown("### Extracted Data")

    # Basic Information
    st.markdown("#### BASIC INFORMATION")

    c1, c2 = st.columns(2)
    with c1:
        st.text_input(
            "Store Name",
            value=st.session_state.extracted_data.get("store_name", ""),
            key="store_name",
            placeholder="Enter store name"
        )
        st.text_input(
            "Receipt Number",
            value=st.session_state.extracted_data.get("receipt_number", ""),
            key="receipt_number",
            placeholder="Enter receipt number"
        )

    with c2:
        st.text_input(
            "Date",
            value=st.session_state.extracted_data.get("date", ""),
            key="date",
            placeholder="DD/MM/YYYY"
        )
        st.text_input(
            "Currency",
            value=st.session_state.extracted_data.get("currency", ""),
            key="currency",
            placeholder="Enter currency"
        )

    # Items
    st.markdown("#### ITEMS")

    items = st.session_state.extracted_data.get("items", [])

    if items:
        for idx, item in enumerate(items, 1):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.text_input(
                    f"Item {idx}",
                    value=item.get("item_name", ""),
                    key=f"item_name_{idx}",
                    placeholder="Item name",
                    label_visibility="visible"
                )
            with c2:
                st.text_input(
                    "Qty",
                    value=item.get("quantity", ""),
                    key=f"quantity_{idx}",
                    placeholder="Qty",
                    label_visibility="visible"
                )
    else:
        st.info("No items extracted yet")

    # Financial Information
    st.markdown("#### FINANCIAL")

    c1, c2 = st.columns(2)
    with c1:
        st.text_input(
            "Taxes",
            value=st.session_state.extracted_data.get("taxes", ""),
            key="taxes",
            placeholder="Tax amount or %"
        )
    with c2:
        st.text_input(
            "Total Amount",
            value=st.session_state.extracted_data.get("total_amount", ""),
            key="total_amount",
            placeholder="Total amount"
        )

# Footer actions
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    if st.button("Clear All Data", use_container_width=True):
        st.session_state.extracted_data = {
            "store_name": "",
            "receipt_number": "",
            "date": "",
            "currency": "",
            "taxes": "",
            "total_amount": "",
            "items": []
        }
        st.rerun()


