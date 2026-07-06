from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf(filename, title, content):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph(f"<b>{title}</b>", styles["Heading1"]))

    story.append(Paragraph(content.replace("\n", "<br/>"), styles["BodyText"]))

    doc.build(story)