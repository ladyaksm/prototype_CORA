import streamlit as st
import requests

BASE_URL = "https://api-cora.mpkmb.com"

def login(username, password):
    # Login pake form-data (OAuth2PasswordRequestForm)
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": username,
                "password": password
            },
            headers={"accept": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                st.session_state.token = token
                return True

        return False

    except Exception as e:
        print("Login error:", e)
        return False


def register(username, password):
    # Register pake query params
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            params={
                "username": username,
                "password": password
            },
            headers={"accept": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "User created":
                return True

        return False

    except Exception as e:
        print("Register error:", e)
        return False