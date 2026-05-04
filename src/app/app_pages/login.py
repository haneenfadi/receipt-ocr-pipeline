import streamlit as st
import requests
def login_page():

    # ----------------------------
    # Page config
    # ----------------------------
    st.set_page_config(page_title="Auth System", layout="centered")

    # ----------------------------
    # Session state init
    # ----------------------------
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None

    BASE_URL = "http://localhost:8000"

    # ----------------------------
    # Header
    # ----------------------------
    st.title("Receipt Vision System | نظام تحليل الفواتير الذكي")
    st.write("قم بتسجيل الدخول أو إنشاء حساب للمتابعة")

    # ----------------------------
    # ----------------------------
    # Mode selector (radio instead of tabs)
    # ----------------------------
    with st.container():
        mode = st.radio(
            "اختر",
            ["تسجيل الدخول", "إنشاء حساب"],
            horizontal=True
        )

    # =========================================================
    # LOGIN
    # =========================================================
    if mode == "تسجيل الدخول":
        st.subheader("تسجيل الدخول")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input(
            "Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True):
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": login_email,
                    "password": login_password
                }
            )

            if response.status_code == 200:
                st.session_state["access_token"] = response.json()["access_token"]
                st.success("Login successful")
                st.rerun()  # redirect to upload page after login
            else:
                st.error("Invalid credentials")

    # =========================================================
    # REGISTER
    # =========================================================
    if mode == "إنشاء حساب":
        st.subheader("إنشاء حساب جديد")

        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input(
            "Password", type="password", key="reg_password")

        if st.button("Register", use_container_width=True):
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": reg_email,
                    "password": reg_password
                }
            )

            if response.status_code == 201:
                # auto-login after register
                login_response = requests.post(
                    f"{BASE_URL}/auth/login",
                    data={
                        "username": reg_email,
                        "password": reg_password
                    }
                )

                if login_response.status_code == 200:
                    st.session_state["access_token"] = login_response.json()[
                        "access_token"]
                    st.success("تم إنشاء الحساب بنجاح ")
                    st.rerun()
                else:
                    st.error("Registered but login failed")
            else:
                st.error(response.text)

    # ----------------------------
    # Block access message
    # ----------------------------
    if st.session_state["access_token"]:
        st.info("You are logged in. Go to Upload page.")
