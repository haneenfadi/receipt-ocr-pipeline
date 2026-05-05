import os
import json
import pandas as pd
import requests
import streamlit as st
from pathlib import Path
from config.settings import settings


CSS_PATH = Path(__file__).resolve().parents[2] / "assets" / "streamlit.css"


def receipts_assistant_page():

    def inject_styles():
        # Load shared CSS from assets
        if CSS_PATH.exists():
            try:
                with open(CSS_PATH, "r", encoding="utf-8") as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            except Exception:
                pass

    def render_header():
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #1B3A6B 0%, #1e4d8c 100%);
                border-radius: 16px;
                padding: 1.6rem 2rem;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 1rem;
            ">
                <div>
                    <div style="font-size: 2rem; margin-bottom: 4px;">🧾</div>
                </div>
                <div>
                    <h1 style="color:white; margin:0; font-size:1.7rem; font-weight:600; font-family:'IBM Plex Sans Arabic',sans-serif;">
                        مساعد الفواتير الذكي
                    </h1>
                    <p style="color:rgba(255,255,255,0.7); margin:0; font-size:14px; font-family:'IBM Plex Sans Arabic',sans-serif;">
                        اسأل عن فواتيرك بالعربية — سنحوّل سؤالك إلى استعلام فوري
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    EXAMPLE_QUESTIONS = [
        "كم مجموع مشترياتي هذا الشهر؟",
        "أي متجر زرته أكثر؟",
        "كم دفعت ضرائب في آخر 3 شهور؟",
        "أعطني أكبر 5 فواتير",
        "مقارنة إنفاقي بين نوفمبر وديسمبر",
        "أي متجر زرته أكثر؟ وأعرض لي كل المنتجات التي اشتريتها",
        "ما المنتجات التي اشتريتها أكثر من مرة؟",
    ]

    def render_sidebar():
        with st.sidebar:
            st.markdown(
                """
                <div style="text-align:center; padding: 1.2rem 0 1.5rem;">
                    <div style="font-size:2.5rem;">🏢</div>
                    <p style="font-size:13px; opacity:0.7; margin:4px 0 0;">نظام إدارة الفواتير</p>
                    <p style="font-size:11px; opacity:0.45; margin:2px 0 0;">v1.0.0</p>
                </div>
                <hr style="border-color:rgba(255,255,255,0.15); margin-bottom:1rem;">
                """,
                unsafe_allow_html=True,
            )

            st.markdown("**أمثلة سريعة**")
            for i, q in enumerate(EXAMPLE_QUESTIONS):
                if st.button(q, key=f"sidebar_example_{i}"):
                    st.session_state["prefill_question"] = q
                    try:
                        st.rerun()
                    except Exception:
                        try:
                            st.experimental_rerun()
                        except Exception:
                            pass

    def render_welcome():
        st.markdown(
            """
            <div style="
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
                padding: 2.5rem 2rem;
                text-align: center;
                margin: 1.5rem 0;
            ">
                <div style="font-size:3rem; margin-bottom:0.75rem;">📊</div>
                <h3 style="color:#1B3A6B; font-family:'IBM Plex Sans Arabic',sans-serif; margin:0 0 0.5rem;">
                    مرحباً بك في مساعد الفواتير
                </h3>
                <p style="color:#718096; font-size:14px; font-family:'IBM Plex Sans Arabic',sans-serif; margin:0 0 1.5rem;">
                    اكتب سؤالك أو اختر أحد الأمثلة للبدء
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_metrics(df: pd.DataFrame):
        numeric_cols = df.select_dtypes(include=["float64", "int64", "int32", "float32"]).columns.tolist()
        if not numeric_cols:
            return
        cols = st.columns(min(4, len(numeric_cols)))
        for i, col in enumerate(numeric_cols[:4]):
            total = df[col].sum()
            label = col.replace("_", " ").title()
            with cols[i]:
                fmt = f"{int(total):,}" if col in ("receipt_count", "item_count", "visits", "id") else f"{total:,.2f}"
                st.metric(label, fmt)

    ARABIC_MONTHS = {
        "january": "يناير", "january_total": "يناير", "jan_total": "يناير", "jan": "يناير",
        "february": "فبراير", "february_total": "فبراير", "feb_total": "فبراير", "feb": "فبراير",
        "march": "مارس", "march_total": "مارس", "mar_total": "مارس", "mar": "مارس",
        "april": "أبريل", "april_total": "أبريل", "apr_total": "أبريل", "apr": "أبريل",
        "may": "مايو", "may_total": "مايو",
        "june": "يونيو", "june_total": "يونيو", "jun_total": "يونيو", "jun": "يونيو",
        "july": "يوليو", "july_total": "يوليو", "jul_total": "يوليو", "jul": "يوليو",
        "august": "أغسطس", "august_total": "أغسطس", "aug_total": "أغسطس", "aug": "أغسطس",
        "september": "سبتمبر", "september_total": "سبتمبر", "sep_total": "سبتمبر", "sep": "سبتمبر",
        "october": "أكتوبر", "october_total": "أكتوبر", "oct_total": "أكتوبر", "oct": "أكتوبر",
        "november": "نوفمبر", "november_total": "نوفمبر", "nov_total": "نوفمبر", "nov": "نوفمبر",
        "december": "ديسمبر", "december_total": "ديسمبر", "dec_total": "ديسمبر", "dec": "ديسمبر",
    }

    BASE_COLUMN_CONFIG = {
        "id": st.column_config.NumberColumn("رقم السجل", format="%d"),
        "store_name": st.column_config.TextColumn("المتجر"),
        "receipt_number": st.column_config.TextColumn("رقم الفاتورة"),
        "date": st.column_config.TextColumn("التاريخ"),
        "currency": st.column_config.TextColumn("العملة", width="small"),
        "taxes": st.column_config.NumberColumn("الضريبة", format="%.2f"),
        "total_amount": st.column_config.NumberColumn("المبلغ الإجمالي", format="%.2f"),
        "item_name": st.column_config.TextColumn("الصنف"),
        "quantity": st.column_config.NumberColumn("الكمية", format="%.0f"),
        "total_taxes": st.column_config.NumberColumn("إجمالي الضرائب", format="%.2f"),
        "receipt_count": st.column_config.NumberColumn("عدد الفواتير", format="%d"),
        "month": st.column_config.TextColumn("الشهر"),
        "month_name": st.column_config.TextColumn("الشهر"),
        "month_number": st.column_config.NumberColumn("رقم الشهر", format="%d"),
        "visits": st.column_config.NumberColumn("الزيارات", format="%d"),
        "average": st.column_config.NumberColumn("المتوسط", format="%.2f"),
        "total": st.column_config.NumberColumn("الإجمالي", format="%.2f"),
        "difference": st.column_config.NumberColumn("الفرق", format="%.2f"),
        "item_count": st.column_config.NumberColumn("عدد الأصناف", format="%d"),
        "created_at": st.column_config.TextColumn("تاريخ الإدخال"),
    }

    def build_column_config(df: pd.DataFrame | None = None) -> dict:
        config = BASE_COLUMN_CONFIG.copy()
        if df is None:
            return config
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ARABIC_MONTHS:
                config[col] = st.column_config.NumberColumn(ARABIC_MONTHS[col_lower], format="%.2f")
            elif col not in config:
                config[col] = st.column_config.TextColumn(col)
        return config

    def render_table(df: pd.DataFrame, key_suffix: str = ""):
        if df.empty:
            st.warning("⚠️ لا توجد نتائج لهذا الاستعلام.")
            return

        display_df = df.drop(columns=["id", "created_at"], errors="ignore")

        render_metrics(display_df)
        dynamic_config = build_column_config(display_df)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={k: v for k, v in dynamic_config.items() if k in display_df.columns},
        )

        csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ تحميل النتائج كـ CSV",
            data=csv_data,
            file_name="receipts_export.csv",
            mime="text/csv",
            key=f"download_{key_suffix}",
        )

    def render_insight(text: str):
        st.markdown(
            f"""
            <div style="
                background: #EBF8FF;
                border-right: 4px solid #2EAADC;
                border-radius: 10px;
                padding: 1rem 1.25rem;
                margin-bottom: 1rem;
                font-family: 'IBM Plex Sans Arabic', sans-serif;
                color: #1A365D;
                font-size: 15px;
                line-height: 1.7;
            ">
                💡 {text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_answer(answer, sql: str = ""):
        if answer is None:
            st.warning("⚠️ لم يتم إرجاع إجابة. حاول إعادة صياغة السؤال.")
            return

        # Try to parse JSON string if answer is a string
        if isinstance(answer, str):
            try:
                answer = json.loads(answer)
            except (json.JSONDecodeError, ValueError):
                # If not valid JSON, treat as plain text insight
                render_insight(answer)
                return

        # Now handle the parsed data (dict, list, etc.)
        if isinstance(answer, dict):
            # If it has insight_ar, render it with optional raw_data table
            if "insight_ar" in answer:
                render_insight(answer["insight_ar"])
                raw = answer.get("raw_data")
                if raw:
                    render_table(pd.DataFrame(raw), key_suffix="dict")
            # Otherwise treat entire dict as a table row
            elif answer:
                render_table(pd.DataFrame([answer]), key_suffix="dict")
            else:
                st.info("لا توجد بيانات لعرضها.")
        elif isinstance(answer, list) and answer:
            render_table(pd.DataFrame(answer), key_suffix="list")
        elif isinstance(answer, (int, float)):
            st.metric("النتيجة", f"{answer:,.2f}")
        else:
            st.info("لا توجد بيانات لعرضها.")

    def main():
        inject_styles()
        render_sidebar()
        render_header()

        if "last_answer" not in st.session_state:
            st.session_state["last_answer"] = None
        if "prefill_question" not in st.session_state:
            st.session_state["prefill_question"] = ""
        if "last_sql" not in st.session_state:
            st.session_state["last_sql"] = ""
        if "history" not in st.session_state:
            st.session_state["history"] = []
        if "question_input" not in st.session_state:
            st.session_state["question_input"] = ""

        prefill = st.session_state.get("prefill_question", "")
        if prefill:
            st.session_state["question_input"] = prefill
            st.session_state["prefill_question"] = ""

        question = st.text_area(
            "اكتب سؤالك هنا",
            placeholder=" مثال:اعطيني أكبر فاتوره عندي",
            height=90,
            key="question_input",
            label_visibility="collapsed",
        )

        col_ask, col_clear, _ = st.columns([1, 1, 6])
        with col_ask:
            ask_clicked = st.button("🔍 اسأل", type="primary", use_container_width=True)
        with col_clear:
            clear_clicked = st.button("✕ مسح", type="secondary", use_container_width=True)

        if clear_clicked:
            st.session_state["question_input"] = ""
            st.session_state["last_answer"] = None
            st.session_state["last_sql"] = ""

        if ask_clicked:
            if not question.strip():
                st.warning("⚠️ الرجاء كتابة سؤال قبل المتابعة.")
            else:
                try:
                    with st.status("جاري المعالجة...", expanded=True) as status:
                        st.write("⚙️ إرسال السؤال إلى الخادم...")
                        headers = {"Authorization": f"Bearer {st.session_state.get('access_token')}"}
                        ask_response = requests.post(
                            f"{settings.BASE_URL}/api/v1/receipts_assistant/ask_question",
                            json={"question": question},
                            headers=headers,
                            timeout=30,
                        )

                        if ask_response.status_code != 200:
                            status.update(label="حدث خطأ", state="error")
                            st.error(f"⚠️ فشل معالجة السؤال: {ask_response.text}")
                        else:
                            payload = ask_response.json()
                            if payload.get("status") == "no_data":
                                status.update(label="لا توجد بيانات", state="error")
                                st.warning(payload.get("message", "No receipts found for this account."))
                            else:
                                answer = payload.get("answer")
                                st.write("✅ جاري عرض الإجابة...")
                                status.update(label="تم بنجاح!", state="complete", expanded=False)
                                st.session_state["history"].append({"q": question, "sql": ""})
                                st.session_state["last_answer"] = answer
                                st.session_state["last_sql"] = ""
                                st.toast("✅ تم العثور على النتائج بنجاح", icon="✅")

                except Exception as e:
                    st.error(f"⚠️ خطأ غير متوقع: {str(e)}\n\nيرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني.")

        if st.session_state["last_answer"] is not None:
            st.markdown("---")
            render_answer(st.session_state["last_answer"], sql=st.session_state["last_sql"])
        elif not ask_clicked:
            render_welcome()

        st.markdown(
            """
            <div class="footer">
                نظام إدارة الفواتير الذكي &nbsp;|&nbsp; v1.0.0 &nbsp;|&nbsp; جميع الحقوق محفوظة
            </div>
            """,
            unsafe_allow_html=True,
        )

    main()
    