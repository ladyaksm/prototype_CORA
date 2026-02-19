import requests

BASE_URL = "http://localhost:8000"  # ganti sesuai backend

def login(username, password):
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            return True
        return False

    except Exception as e:
        print("Login error:", e)
        return False


def register(username, password):
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            return True
        return False

    except Exception as e:
        print("Register error:", e)
        return False
