import streamlit as st
from utils.auth import login, register
from chat.init import render_chat


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "username" not in st.session_state:
    st.session_state.username = ""


# LOGIN / REGISTER
if not st.session_state.authenticated:

    if st.session_state.page == "login":

        st.title("CORA Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login"):
                if login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.page = "chat"
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Username atau password salah")

        with col2:
            if st.button("Register"):
                st.session_state.page = "register"
                st.rerun()

    elif st.session_state.page == "register":

        st.title("CORA Register")

        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Create Account"):
                if register(new_username, new_password):
                    st.success("Akun berhasil dibuat. Silakan login.")
                else:
                    st.error("Username sudah digunakan.")

        with col2:
            if st.button("Back to Login"):
                st.session_state.page = "login"
                st.rerun()

# CHAT PAGE
elif st.session_state.page == "chat":

    # SIDEBAR
    with st.sidebar:

        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    render_chat()
