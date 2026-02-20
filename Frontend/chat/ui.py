import streamlit as st
import html
from .state import init_chat_state
from utils.api import api_request, upload_pdf
import requests

def render_chat():
    init_chat_state()

    if "pending_pdf" not in st.session_state:
        st.session_state.pending_pdf = None
    if "pending_pdf_name" not in st.session_state:
        st.session_state.pending_pdf_name = None

    # LOAD CHAT HISTORY
    if len(st.session_state.messages) == 0:
        response = api_request("GET", "/chat/history")
        if response and response.status_code == 200:
            history = response.json()
            if isinstance(history, list):
                for item in history:
                    st.session_state.messages.append({"role": "user", "content": item.get("user", "")})
                    st.session_state.messages.append({"role": "assistant", "content": item.get("CORA", "")})

    # CSS
    st.markdown("""
    <style>
    [data-testid="stHeader"] {
        background-color: #0E1117 !important;
        border-bottom: 1px solid #262730 !important;
        z-index: 9999 !important;
    }
    [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 0rem !important; }

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
        from { opacity: 0; transform: translateY(5px); }
        to   { opacity: 1; transform: translateY(0); }
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
    .chat-row { display: flex; }

    /* ── Fix gap abu-abu di kolom tombol + ── */

    /* Hapus background & padding dari stBottom (area fixed bawah) */
    [data-testid="stBottom"] {
        background: transparent !important;
        padding: 0 !important;
    }
    /* Hapus background kolom kecil tempat tombol + */
    [data-testid="stBottom"] [data-testid="stHorizontalBlock"] {
        gap: 4px !important;
        align-items: flex-end !important;
        background: transparent !important;
    }
    [data-testid="stBottom"] [data-testid="column"] {
        background: transparent !important;
        padding: 0 !important;
    }
    /* Styling tombol + */
    [data-testid="stBottom"] [data-testid="column"]:first-child button {
        width: 44px !important;
        height: 44px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 20px !important;
        border: 1.5px solid #d1d5db !important;
        background: white !important;
        color: #6b7280 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
        min-height: unset !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stBottom"] [data-testid="column"]:first-child button:hover {
        color: #2563eb !important;
        border-color: #2563eb !important;
        background: #f0f4ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    st.markdown("""
    <style>
    [data-testid="stHeader"]::before {
        content: "CORA - Corporate University Assistant";
        display: block;
        color: white;
        font-size: 20px;
        font-weight: 600;
        padding: 16px 40px;
        font-family: inherit;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chat-container" style="margin-top: 80px;">', unsafe_allow_html=True)

    # GREETING
    if len(st.session_state.messages) == 0:
        st.markdown("### Hai, aku CORA 👋")
        st.markdown("Aku akan menemanimu merancang Corporate University sebelum sesi konsultasi profesional.")

    # RENDER CHAT HISTORY
    for msg in st.session_state.messages:
        safe_content = html.escape(msg["content"])
        bubble_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(f"""
        <div class="chat-row">
            <div class="chat-bubble {bubble_class}">{safe_content}</div>
        </div>
        """, unsafe_allow_html=True)

    # BLUEPRINT BUTTON
    if st.session_state.chat_count >= 5 and not st.session_state.blueprint_generated:
        st.session_state.show_blueprint_button = True

    if st.session_state.show_blueprint_button and not st.session_state.blueprint_generated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Mau Generate Blueprint?"):
                response = api_request("POST", "/chat/blueprint", {"inputUser": "Generate blueprint berdasarkan diskusi"})
                if response and response.status_code == 200:
                    data = response.json()
                    template_response = "\n".join(data.get("response", []))
                else:
                    template_response = "Gagal generate blueprint."
                st.session_state.blueprint_content = template_response
                st.session_state.blueprint_generated = True
                st.session_state.show_blueprint_button = False
                st.session_state.messages.append({"role": "assistant", "content": template_response})
                st.session_state.interaction_locked = True
                st.rerun()

    # AFTER BLUEPRINT
    if st.session_state.blueprint_generated:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗣 Chat Sesi Konsultasi"):
                response = api_request("GET", "/chat/consultation")
                consult_msg = response.json().get("response", "Tidak ada kontak.") if response and response.status_code == 200 else "Gagal mengambil kontak."
                st.session_state.messages.append({"role": "assistant", "content": consult_msg})
                st.session_state.interaction_locked = True
                st.rerun()
        with col2:
            if st.button("📄 Export Blueprint"):
                response = api_request("GET", "/chat/blueprint/export", stream=True)
                if response and response.status_code == 200:
                    st.download_button(label="Download CORA Blueprint PDF", data=response.content, file_name="CORA_Blueprint.pdf", mime="application/pdf")
                else:
                    st.error("Gagal export blueprint.")

    # SESSION LOCK
    if st.session_state.interaction_locked:
        st.info("Sesi telah selesai. Untuk memulai ulang, silakan refresh halaman.")

    # FILE UPLOADER — muncul di atas chat input kalau toggle aktif
    if st.session_state.get("show_file_uploader", False) and not st.session_state.interaction_locked:
        uploaded_file = st.file_uploader(
            "Pilih file PDF",
            type=["pdf"],
            key="pdf_uploader",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            if st.session_state.pending_pdf_name != uploaded_file.name:
                st.session_state.pending_pdf = uploaded_file.read()
                st.session_state.pending_pdf_name = uploaded_file.name
        if st.session_state.pending_pdf_name:
            st.caption(f"📎 **{st.session_state.pending_pdf_name}** siap dikirim — tulis pesan lalu tekan Enter.")

    # CHAT INPUT
    # Pakai st.columns tapi CSS di atas sudah hapus background abu-abu
    if not st.session_state.interaction_locked:
        col_plus, col_chat = st.columns([1, 12])
        with col_plus:
            if st.button("＋", key="btn_upload_toggle", help="Upload PDF ke CORA"):
                st.session_state.show_file_uploader = not st.session_state.get("show_file_uploader", False)
                if not st.session_state.show_file_uploader:
                    st.session_state.pending_pdf = None
                    st.session_state.pending_pdf_name = None
                st.rerun()
        with col_chat:
            prompt = st.chat_input(
                "Tanyakan sesuatu tentang Corporate University...",
                disabled=False
            )
    else:
        prompt = st.chat_input(
            "Tanyakan sesuatu tentang Corporate University...",
            disabled=True
        )

    # HANDLE SEND
    if prompt:
        user_display = prompt
        if st.session_state.pending_pdf_name:
            user_display = f"{prompt}\n📎 {st.session_state.pending_pdf_name}"

        st.session_state.messages.append({"role": "user", "content": user_display})
        st.session_state.chat_count += 1

        if st.session_state.pending_pdf is not None:
            with st.spinner("Mengupload PDF..."):
                pdf_response = upload_pdf(st.session_state.pending_pdf, st.session_state.pending_pdf_name)
            if pdf_response and pdf_response.status_code == 200:
                pdf_data = pdf_response.json()
                if pdf_data.get("status") == "success":
                    notif_msg = pdf_data.get("message", "PDF berhasil diunggah.")
                    st.session_state.messages.append({"role": "assistant", "content": f"📄 {notif_msg}"})
                    st.session_state.pending_pdf = None
                    st.session_state.pending_pdf_name = None
                    st.session_state.show_file_uploader = False
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "❌ Gagal upload PDF: " + pdf_data.get("message", "Unknown error")})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "❌ Gagal menghubungi server saat upload PDF."})

        response = api_request("POST", "/chat/message", {"chatUser": prompt})
        if response and response.status_code == 200:
            bot_reply = response.json().get("response", "Tidak ada balasan.")
        else:
            bot_reply = "Terjadi kesalahan pada server."

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)