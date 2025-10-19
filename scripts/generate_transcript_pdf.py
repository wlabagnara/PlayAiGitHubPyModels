"""Generate chat_transcript.pdf from chat_transcript.md using ReportLab.

This is a small utility that reads the markdown file, strips basic markdown
syntax for headings/code blocks and writes a simple flowing PDF.

Note: This is intentionally lightweight and will not render complex markdown.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import textwrap

INPUT = "../chat_transcript.md"
OUTPUT = "../chat_transcript.pdf"


def md_to_paragraphs(md_text: str):
    # Very simple markdown -> paragraphs converter
    lines = md_text.splitlines()
    paras = []
    buf = []
    for line in lines:
        if line.strip() == "":
            if buf:
                paras.append(" ".join(buf).strip())
                buf = []
            continue
        # strip heading markers
        if line.startswith("#"):
            if buf:
                paras.append(" ".join(buf).strip())
                buf = []
            paras.append(line.lstrip('#').strip().upper())
            continue
        # strip code fences
        if line.startswith('```'):
            continue
        # simple bullet marker
        if line.strip().startswith('- '):
            buf.append('\u2022 ' + line.strip()[2:])
        else:
            buf.append(line.strip())
    if buf:
        paras.append(" ".join(buf).strip())
    return paras


def build_pdf():
    with open(INPUT, "r", encoding="utf-8") as f:
        md = f.read()
    paras = md_to_paragraphs(md)

    doc = SimpleDocTemplate(OUTPUT, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    normal = styles["BodyText"]
    heading = ParagraphStyle('Heading1', parent=styles['Heading1'], spaceAfter=12)

    flow = []
    for p in paras:
        if p == p.upper() and len(p.split()) < 8:
            flow.append(Paragraph(p, heading))
        else:
            # wrap long lines for readability
            wrapped = textwrap.fill(p, width=100)
            flow.append(Paragraph(wrapped, normal))
        flow.append(Spacer(1, 6))

    doc.build(flow)
    print(f"Wrote {OUTPUT}")


if __name__ == '__main__':
    build_pdf()
