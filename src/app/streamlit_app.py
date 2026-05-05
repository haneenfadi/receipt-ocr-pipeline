import streamlit as st
from app_pages.login import login_page
from app_pages.upload import upload_page
from app_pages.ask_receipts import receipts_assistant_page

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Receipt Vision | نظام الفواتير الذكي",
    layout="wide"
)

# -----------------------------
# INIT STATE
# -----------------------------
if "page" not in st.session_state:
    st.session_state["page"] = "تسجيل الدخول"

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None


# -----------------------------
# SIDEBAR MENU
# -----------------------------
menu_pages = ["تسجيل الدخول", "رفع الفواتير", "مساعد الفواتير"]

page = st.sidebar.radio(
    "القائمة",
    menu_pages,
    index=menu_pages.index(st.session_state["page"])
)

st.session_state["page"] = page


# -----------------------------
# AUTH GUARD (IMPORTANT)
# -----------------------------
if page != "تسجيل الدخول" and not st.session_state["access_token"]:
    st.warning("يرجى تسجيل الدخول أولاً")
    st.session_state["page"] = "تسجيل الدخول"
    login_page()
    st.stop()


# -----------------------------
# ROUTER
# -----------------------------
if page == "تسجيل الدخول":
    login_page()

elif page == "رفع الفواتير":
    upload_page()

elif page == "مساعد الفواتير":
    receipts_assistant_page()
