# Frontend/utils/api.py
import requests
import streamlit as st

BASE_URL = "https://api-cora.mpkmb.com"

def api_request(method, endpoint, data=None, stream=False):
    headers = {
        "accept": "application/json"
    }

    # Attach token if exists
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            return requests.get(url, headers=headers, stream=stream)
        if method == "POST":
            return requests.post(url, json=data, headers=headers)
    except Exception as e:
        print("API Error:", e)
        return None

def upload_pdf(file_bytes, filename):
    """Upload PDF file ke endpoint /chat/upload_PDF"""
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    url = f"{BASE_URL}/chat/upload_PDF"

    try:
        files = {
            "file": (filename, file_bytes, "application/pdf")
        }
        response = requests.post(url, files=files, headers=headers)
        return response
    except Exception as e:
        print("Upload PDF Error:", e)
        return None