import streamlit as st
import html
from .state import init_chat_state
from utils.api import api_request, upload_pdf
import io
import requests

def render_chat():
    init_chat_state()

    # LOAD CHAT HISTORY
    if len(st.session_state.messages) == 0:
        response = api_request("GET", "/chat/history")
        if response and response.status_code == 200:
            history = response.json()
            if isinstance(history, list):
                for item in history:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": item.get("user", "")
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": item.get("CORA", "")
                    })

    # CSS FIXED HEADER + CHAT UI
    st.markdown("""
    <style>
    [data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 0rem !important;
    }
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
    .header-title {
        color: white;
        font-size: 20px;
        font-weight: 600;
    }
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

    /* Styling untuk area upload PDF */
    .pdf-upload-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 12px;
        background-color: #1f2937;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #374151;
    }
    .pdf-upload-label {
        color: #9ca3af;
        font-size: 13px;
    }
    .pdf-success {
        color: #34d399;
        font-size: 13px;
        font-weight: 500;
    }
    .pdf-error {
        color: #f87171;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    st.markdown("""
    <div class="header-fixed">
        <div class="header-title">
            CORA - Corporate University Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # GREETING
    if len(st.session_state.messages) == 0:
        st.markdown("### Hai, aku CORA 👋")
        st.markdown("Aku akan menemanimu merancang Corporate University sebelum sesi konsultasi profesional.")

    # RENDER CHAT HISTORY
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

    # SHOW BLUEPRINT BUTTON
    if st.session_state.chat_count >= 5 and not st.session_state.blueprint_generated:
        st.session_state.show_blueprint_button = True

    if st.session_state.show_blueprint_button and not st.session_state.blueprint_generated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Mau Generate Blueprint?"):
                response = api_request(
                    "POST", "/chat/blueprint",
                    {"inputUser": "Generate blueprint berdasarkan diskusi"}
                )
                if response and response.status_code == 200:
                    data = response.json()
                    blueprint_list = data.get("response", [])
                    template_response = "\n".join(blueprint_list)
                else:
                    template_response = "Gagal generate blueprint."

                st.session_state.blueprint_content = template_response
                st.session_state.blueprint_generated = True
                st.session_state.show_blueprint_button = False
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": template_response
                })
                st.session_state.interaction_locked = True
                st.rerun()

    # AFTER BLUEPRINT GENERATED
    if st.session_state.blueprint_generated:
        st.markdown("---")
        col1, col2 = st.columns(2)

        # CONSULTATION BUTTON
        with col1:
            if st.button("🗣 Chat Sesi Konsultasi"):
                response = api_request("GET", "/chat/consultation")
                if response and response.status_code == 200:
                    data = response.json()
                    consult_msg = data.get("response", "Tidak ada kontak.")
                else:
                    consult_msg = "Gagal mengambil kontak."
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": consult_msg
                })
                st.session_state.interaction_locked = True
                st.rerun()

        # EXPORT PDF BUTTON
        with col2:
            if st.button("📄 Export Blueprint"):
                response = api_request(
                    "GET", "/chat/blueprint/export",
                    stream=True
                )
                if response and response.status_code == 200:
                    st.download_button(
                        label="Download CORA Blueprint PDF",
                        data=response.content,
                        file_name="CORA_Blueprint.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Gagal export blueprint.")

    # SESSION LOCK INFO
    if st.session_state.interaction_locked:
        st.info("Sesi telah selesai. Untuk memulai ulang, silakan refresh halaman.")

    # Layout: kolom kecil buat tombol "+", kolom besar buat chat input
    col_plus, col_input = st.columns([1, 11])

    with col_plus:
        # Tombol "+" toggle show/hide file uploader
        if not st.session_state.interaction_locked:
            if st.button("➕", help="Upload PDF ke CORA", key="btn_upload_toggle"):
                st.session_state.show_file_uploader = not st.session_state.get("show_file_uploader", False)

    with col_input:
        prompt = st.chat_input(
            "Tanyakan sesuatu tentang Corporate University...",
            disabled=st.session_state.interaction_locked
        )

    # FILE UPLOADER — muncul di atas chat input kalau toggle aktif
    if st.session_state.get("show_file_uploader", False) and not st.session_state.interaction_locked:
        uploaded_file = st.file_uploader(
            "Upload dokumen PDF untuk CORA",
            type=["pdf"],
            key="pdf_uploader",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            # Cegah upload ulang file yang sama
            if st.session_state.get("last_uploaded_pdf") != uploaded_file.name:
                with st.spinner("Mengupload PDF..."):
                    file_bytes = uploaded_file.read()
                    response = upload_pdf(file_bytes, uploaded_file.name)

                if response and response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        st.session_state.last_uploaded_pdf = uploaded_file.name
                        st.session_state.show_file_uploader = False
                        # Tambahkan notifikasi ke chat
                        success_msg = f"📄 PDF **{uploaded_file.name}** berhasil diunggah ke CORA."
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": success_msg
                        })
                        st.rerun()
                    else:
                        st.error("Upload gagal: " + data.get("message", "Unknown error"))
                else:
                    st.error("Gagal menghubungi server. Coba lagi.")

    # HANDLE CHAT INPUT
    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        st.session_state.chat_count += 1

        response = api_request(
            "POST", "/chat/message",
            {"chatUser": prompt}
        )
        if response and response.status_code == 200:
            data = response.json()
            bot_reply = data.get("response", "Tidak ada balasan.")
        else:
            bot_reply = "Terjadi kesalahan pada server."

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply
        })
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)