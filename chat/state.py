import streamlit as st

def init_chat_state():
    defaults = {
        "messages": [],
        "chat_count": 0,
        "show_blueprint_button": False,
        "blueprint_generated": False,
        "blueprint_content": "",
        "interaction_locked": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
