import streamlit as st
import requests
from PIL import Image
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def upload_page():

    st.set_page_config(
        page_title="نظام استخراج بيانات الفواتير",
        page_icon="",
        layout="wide",
        initial_sidebar_state="collapsed"
    )


    with open(r"src/assets/streamlit.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .upload-hero {
            background: linear-gradient(135deg, #1B3A6B 0%, #1E4D8C 100%);
            border-radius: 14px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
            color: white;
            text-align: center;
        }
        .upload-hero h2 {
            margin: 0;
            font-size: 1.55rem;
            font-weight: 600;
        }
        .upload-hero p {
            margin: 0.35rem 0 0;
            opacity: 0.86;
            font-size: 0.92rem;
        }
        .section-title {
            margin: 0 0 0.65rem;
            color: #1B3A6B;
            font-weight: 700;
            font-size: 1.08rem;
        }
        .section-subtitle {
            margin: 0.4rem 0 0.75rem;
            color: #4A5568;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .section-title--inset,
        .section-subtitle--inset {
            padding-right: 0.65rem;
        }
        .section-title--right-inset,
        .section-subtitle--right-inset {
            padding-right: 2rem;
        }
        </style>
        <div class="upload-hero">
            <h2>استخرج بيانات فواتيرك مع نظام  Receipt Vision </h2>
            <p>ارفع صورة الفاتورة وسيتم تعبئة الحقول تلقائياً بشكل منظم</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    def sync_form_from_extracted_data() -> None:
        data = st.session_state.get("extracted_data", {}) or {}
        st.session_state["store_name"] = data.get("store_name", "") or ""
        st.session_state["receipt_number"] = data.get("receipt_number", "") or ""
        st.session_state["date"] = data.get("date", "") or ""
        st.session_state["currency"] = data.get("currency", "") or ""
        st.session_state["taxes"] = data.get("taxes", "") or ""
        st.session_state["total_amount"] = data.get("total_amount", "") or ""

        items_data = data.get("items", []) or []

        # Clean old item widgets when a new response has fewer rows.
        stale_index = len(items_data) + 1
        while f"item_name_{stale_index}" in st.session_state or f"quantity_{stale_index}" in st.session_state:
            st.session_state.pop(f"item_name_{stale_index}", None)
            st.session_state.pop(f"quantity_{stale_index}", None)
            stale_index += 1

        for idx, item in enumerate(items_data, 1):
            st.session_state[f"item_name_{idx}"] = item.get("item_name", "") or ""
            st.session_state[f"quantity_{idx}"] = item.get("quantity", "") or ""

    sync_form_from_extracted_data()

    if not st.session_state.get("access_token"):
        st.warning("سجل الدخول من فضلك")

        st.session_state["page"] = "تسجيل الدخول"
        st.rerun()

        st.stop()
    # Layout
    col1, col2 = st.columns([0.95, 1.05], gap="large")
    # col1, col2 = st.columns([0.95, 1.05])

    with col1:
        st.markdown('<div class="section-title section-title--inset"><br>ارفع الصورة</br></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle section-subtitle--inset">اختر صورة واضحة ثم اضغط بدء الاستخراج</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "اختر صورة الفاتورة",
            type=['jpg', 'jpeg', 'png'],
            help="الصيغ المدعومة: JPG، JPEG، PNG"
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("بدء الاستخراج", type="primary", use_container_width=True):
                with st.spinner("جاري المعالجة..."):
                    try:
                        uploaded_file.seek(0)

                        files = {
                            "file": ("receipt.jpg", uploaded_file, "image/jpeg")}
                    
                        headers = {
                            "Authorization": f"Bearer {st.session_state['access_token']}"}
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
                                "items": result.get("items", [])
                            }
                            sync_form_from_extracted_data()

                            st.rerun()
                        else:
                            st.error(
                                f"خطأ: تعذرت معالجة الفاتورة (الحالة {response.status_code})")

                    except Exception as e:
                        st.error(f"خطأ: {str(e)}")
        else:
            st.info("ابدأ برفع صورة فاتورة للمعالجة")

    with col2:
    
        # Basic Information
        st.markdown("#### بيانات الفاتورة")

        c1, c2 = st.columns(2)
        with c1:
            st.text_input(
                "اسم المتجر",
                key="store_name",
                placeholder="أدخل اسم المتجر"
            )
            st.text_input(
                "رقم الفاتورة",
                key="receipt_number",
                placeholder="أدخل رقم الفاتورة"
            )

        with c2:
            st.text_input(
                "التاريخ",
                key="date",
                placeholder="يوم/شهر/سنة"
            )
            st.text_input(
                "العملة",
                key="currency",
                placeholder="أدخل العملة"
            )

        # Items
        st.markdown("#### الأصناف")

        items = st.session_state.extracted_data.get("items", [])

        if items:
            for idx, item in enumerate(items, 1):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.text_input(
                        f"الصنف {idx}",
                        key=f"item_name_{idx}",
                        placeholder="اسم الصنف",
                        label_visibility="visible"
                    )
                with c2:
                    st.text_input(
                        "الكمية",
                        key=f"quantity_{idx}",
                        placeholder="الكمية",
                        label_visibility="visible"
                    )
        else:
            st.info("لا توجد أصناف مستخرجة بعد")

        # Financial Information
        st.markdown("#### القيم المالية")

        c1, c2 = st.columns(2)
        with c1:
            st.text_input(
                "الضرائب",
                key="taxes",
                placeholder="قيمة الضريبة أو النسبة"
            )
        with c2:
            st.text_input(
                "المبلغ الإجمالي",
                key="total_amount",
                placeholder="المبلغ الإجمالي"
            )

    # Footer actions
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1.5, 2])
    
    with col1:
        # Generate CSV data
        extracted_data = st.session_state.extracted_data
        if extracted_data.get("store_name") or extracted_data.get("receipt_number"):
            # Create DataFrame from extracted data
            df_dict = {
                "اسم المتجر": [extracted_data.get("store_name", "")],
                "رقم الفاتورة": [extracted_data.get("receipt_number", "")],
                "التاريخ": [extracted_data.get("date", "")],
                "العملة": [extracted_data.get("currency", "")],
                "الضرائب": [extracted_data.get("taxes", "")],
                "المبلغ الإجمالي": [extracted_data.get("total_amount", "")],
            }
            df = pd.DataFrame(df_dict)
            csv_data = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            
            st.download_button(
                label="⬇️ تحميل CSV",
                data=csv_data,
                file_name=f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        if st.button("مسح البيانات", use_container_width=True, key="clear_btn"):
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


