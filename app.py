import streamlit as st
from utils.auth import login, register
from chat import render_chat


# ini state 
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "username" not in st.session_state:
    st.session_state.username = ""


# login
if not st.session_state.authenticated:

    if st.session_state.page == "login":

        st.title("CORA Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login"):
                success = login(username, password)
                if not success:
                    st.error("Username atau password salah")
                else:
                    st.session_state.authenticated = True
                    st.session_state.page = "chat"
                    st.session_state.username = username
                    st.rerun()

        with col2:
            if st.button("Register"):
                st.session_state.page = "register"
                st.rerun()

    # regsiter
    elif st.session_state.page == "register":

        st.title("CORA Register")

        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Create Account"):
                success = register(new_username, new_password)
                if success:
                    st.success("Akun berhasil dibuat. Silakan login.")
                else:
                    st.error("Username sudah digunakan.")

        with col2:
            if st.button("Back to Login"):
                st.session_state.page = "login"
                st.rerun()


# chat page
elif st.session_state.page == "chat":

    # logout button di atas
    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.page = "login"

            # Reset session chat juga
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.rerun()

    render_chat()
