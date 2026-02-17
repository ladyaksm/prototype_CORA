import streamlit as st
from .state import init_chat_state
from .pdf import generate_pdf


def render_chat():

    init_chat_state()

    # FIXED HEADER CSS
    st.markdown("""
<style>

/* Hide default Streamlit header */
[data-testid="stHeader"] {
    display: none;
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
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show blueprint button after 5 chats
    if st.session_state.chat_count >= 5 and not st.session_state.blueprint_generated:
        st.session_state.show_blueprint_button = True

    # Generate Blueprint Button
    if st.session_state.show_blueprint_button and not st.session_state.blueprint_generated:

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Mau Generate Blueprint?"):

                template_response = """
Draft Blueprint Corporate University

Ini masih hanya prototipe, nanti akan dikembangkan lagi ya...
"""

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

                consult_msg = "Silahkan hubungi tim kami untuk sesi konsultasi lanjutan."

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

        response = "Terima kasih atas pertanyaannya. CORA akan membantu kebutuhan awal Anda."

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
