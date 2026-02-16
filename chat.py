import streamlit as st
import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


# function generate pdf
def generate_pdf(content):

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_file.name, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>CORA Blueprint Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)

    return temp_file.name

# function render chat 
def render_chat():

    st.title("CORA - Corporate University Assistant")

    # init state 
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_count" not in st.session_state:
        st.session_state.chat_count = 0

    if "show_blueprint_button" not in st.session_state:
        st.session_state.show_blueprint_button = False

    if "blueprint_generated" not in st.session_state:
        st.session_state.blueprint_generated = False

    if "blueprint_content" not in st.session_state:
        st.session_state.blueprint_content = ""

    if "interaction_locked" not in st.session_state:
        st.session_state.interaction_locked = False

    # greeting
    if len(st.session_state.messages) == 0:
        st.markdown("### Hai, aku CORA 👋")
        st.markdown("Aku akan menemanimu merancang Corporate University sebelum sesi konsultasi profesional.")

    # chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # cek apakah sudah mencapai batas interaksi 
    if st.session_state.chat_count >= 5 and not st.session_state.blueprint_generated:
        st.session_state.show_blueprint_button = True

    # button generate blueprint 
    if st.session_state.show_blueprint_button and not st.session_state.blueprint_generated:

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(" Mau Generate Blueprint?"):

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

    # setelah blueprint di-generate,\
    if st.session_state.blueprint_generated:

        st.markdown("---")

        col1, col2 = st.columns(2)

        # button untuk sesi konsultasi
        with col1:
            if st.button("🗣 Chat Sesi Konsultasi"):

                consult_msg = "Silahkan anda menghubungi contact berikut ....."

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": consult_msg
                })

                st.session_state.interaction_locked = True  # lock chat
                st.rerun()

        # button untuk export blueprint ke PDF
        with col2:
            pdf_path = generate_pdf(st.session_state.blueprint_content)

            with open(pdf_path, "rb") as f:
                if st.download_button(
                    label="📄 Export Blueprint",
                    data=f,
                    file_name="CORA_Blueprint.pdf",
                    mime="application/pdf"
                ):
                    st.session_state.interaction_locked = True  # lock chat
                    st.rerun()


    # menutup interaksi jika sudah selesai
    if st.session_state.interaction_locked:
        st.info("Sesi telah selesai. Untuk memulai ulang, silakan refresh halaman.")

    # chat input untuk user  jika interaksi belum di-lock
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
