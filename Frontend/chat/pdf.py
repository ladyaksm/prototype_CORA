import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


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
