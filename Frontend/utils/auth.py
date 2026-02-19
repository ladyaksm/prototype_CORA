# Frontend/utils/auth.py
import streamlit as st
from .api import api_request


def login(username, password):

    response = api_request(
        "POST",
        "/auth/login",
        {"username": username, "password": password}
    )

    if not response:
        return False

    if response.status_code == 200:
        data = response.json()

        # kalau backend return token string
        if isinstance(data, str):
            st.session_state.token = data
            return True

        # kalau backend return object success
        if isinstance(data, dict) and data.get("status") == "success":
            st.session_state.token = data.get("token")
            return True

        # kalau invalid credentials
        if isinstance(data, dict) and data.get("status_code") == 401:
            return False

    return False


def register(username, password):

    response = api_request(
        "POST",
        "/auth/register",
        {"username": username, "password": password}
    )

    if response and response.status_code == 200:
        return True

    return False
