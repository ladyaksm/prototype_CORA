import streamlit as st
from .state import init_chat_state
from .pdf import generate_pdf
import html
import requests

BASE_URL = "http://localhost:8000"

def render_chat():

    init_chat_state()

    if len(st.session_state.messages) == 0:
        try:
            response = requests.get(f"{BASE_URL}/chat/history")
            if response.status_code == 200:
                history = response.json()
                for item in history:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": item["message"]
                    })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": item["botResponse"]
                })
        except:
            pass


    # FIXED HEADER CSS
    st.markdown("""
<style>

/* Hide default Streamlit header */
[data-testid="stHeader"] {
    background: transparent;
}

/* Remove top padding */
.block-container {
    padding-top: 0rem !important;
}

/* Custom Header */
.header-fixed {
    position: fixed;
    top: 0;
    left: 16rem;
    right: 0;
    background-color: #0E1117;
    padding: 20px 40px;
    z-index: 9999;
    border-bottom: 1px solid #262730;
}

/* Title */
.header-title {
    color: white;
    font-size: 20px;
    font-weight: 600;
}

/* Push content down */
.chat-container {
    margin-top: 90px;
}

.chat-bubble {
    padding: 12px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
    max-width: 70%;
    word-wrap: break-word;
    font-size: 15px;
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(5px);}
    to {opacity: 1; transform: translateY(0);}
}

.user-bubble {
    background-color: #2563eb;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.assistant-bubble {
    background-color: #1f2937;
    color: white;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

.chat-row {
    display: flex;
}


</style>
""", unsafe_allow_html=True)



    st.markdown("""
<div class="header-fixed">
    <div class="header-title">
        CORA - Corporate University Assistant
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)


    # Greeting
    if len(st.session_state.messages) == 0:
        st.markdown("### Hai, aku CORA 👋")
        st.markdown("Aku akan menemanimu merancang Corporate University sebelum sesi konsultasi profesional.")

    # Chat history
    for msg in st.session_state.messages:
        safe_content = html.escape(msg["content"])
        
        if msg["role"] == "user":
            st.markdown(f"""
        <div class="chat-row">
            <div class="chat-bubble user-bubble">
                {safe_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
        <div class="chat-row">
            <div class="chat-bubble assistant-bubble">
                {safe_content}
            </div>
        </div>
        """, unsafe_allow_html=True)



    # Show blueprint button after 5 chats
    if st.session_state.chat_count >= 5 and not st.session_state.blueprint_generated:
        st.session_state.show_blueprint_button = True

    # Generate Blueprint Button
    if st.session_state.show_blueprint_button and not st.session_state.blueprint_generated:

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Mau Generate Blueprint?"):

                try:
                    response = requests.post(f"{BASE_URL}/chat/blueprint")
                    if response.status_code == 200:
                        template_response = response.json()
                    else:
                        template_response = "Gagal generate blueprint."

                except:
                    template_response = "Server tidak dapat dihubungi."

                st.session_state.blueprint_content = template_response
                st.session_state.blueprint_generated = True
                st.session_state.show_blueprint_button = False

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": template_response
                })

                st.session_state.interaction_locked = True
                st.rerun()

    # After Blueprint Generated
    if st.session_state.blueprint_generated:

        st.markdown("---")

        col1, col2 = st.columns(2)

        # Konsultasi
        with col1:
            if st.button("🗣 Chat Sesi Konsultasi"):

                try:
                    response = requests.get(f"{BASE_URL}/chat/consult")
                    if response.status_code == 200:
                        consult_msg = response.json()["contact"]
                    else:
                        consult_msg = "Gagal mengambil kontak."
                except:
                    consult_msg = "Server tidak dapat dihubungi."

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": consult_msg
                })

                st.session_state.interaction_locked = True
                st.rerun()

        # Export PDF
        with col2:
            pdf_path = generate_pdf(st.session_state.blueprint_content)

            with open(pdf_path, "rb") as f:
                if st.download_button(
                    label="📄 Export Blueprint",
                    data=f,
                    file_name="CORA_Blueprint.pdf",
                    mime="application/pdf"
                ):
                    st.session_state.interaction_locked = True
                    st.rerun()

    # Lock message
    if st.session_state.interaction_locked:
        st.info("Sesi telah selesai. Untuk memulai ulang, silakan refresh halaman.")

    # Chat input
    prompt = st.chat_input(
        "Tanyakan sesuatu tentang Corporate University...",
        disabled=st.session_state.interaction_locked
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        st.session_state.chat_count += 1

        try:
            response = requests.post(
                f"{BASE_URL}/chat/message",
                json={"message": prompt}
    )

            if response.status_code == 200:
                bot_reply = response.json()
            else:
                bot_reply = "Terjadi kesalahan pada server."

        except Exception as e:
            bot_reply = "Server tidak dapat dihubungi."

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply
        })

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
