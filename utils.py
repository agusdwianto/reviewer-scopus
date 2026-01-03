from typing import BinaryIO
import PyPDF2
from docx import Document


def extract_text(file: BinaryIO) -> str:
    """Extract text from .docx or .pdf file-like objects.
    Guards against image-only PDF pages (None returns) and returns concatenated text.
    """
    name = getattr(file, 'name', '')
    if name.endswith('.docx'):
        return "\n".join([p.text for p in Document(file).paragraphs])
    elif name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        texts = []
        for page in reader.pages:
            try:
                t = page.extract_text()
            except Exception:
                t = None
            if t:
                texts.append(t)
        return "\n".join(texts)
    return ""


def file_too_large(file: BinaryIO, max_mb: int = 20) -> bool:
    """Return True if file (UploadedFile) is larger than max_mb.
    Uses getbuffer() which is available on Streamlit's UploadedFile.
    """
    try:
        size = len(file.getbuffer())
        return size > max_mb * 1024 * 1024
    except Exception:
        return False


import io


def generate_pdf_report(content: str, user_name: str = None, scores: dict = None) -> bytes:
    """Generate a professional review PDF and return bytes.

    Preferred behavior: use ReportLab (good Unicode support) when available.
    Fallback: use fpdf2 (latin-1, may drop non-Latin characters).

    Raises:
        RuntimeError: if neither `reportlab` nor `fpdf2` is installed.
    """
    # Prefer ReportLab for Unicode-safe PDFs
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        # Fallback to fpdf2 if reportlab is not available
        try:
            from fpdf import FPDF
        except ImportError as e:
            raise RuntimeError("PDF generation requires 'reportlab' (preferred) or 'fpdf2'. Install with: pip install reportlab or pip install fpdf2") from e

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "MANUSCRIPT ASSESSMENT REPORT", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        header = "Standard: Scopus/Web of Science Q1 Quality"
        if user_name:
            header = f"Prepared for: {user_name} | {header}"
        pdf.cell(0, 10, header, ln=True, align='C')
        pdf.ln(8)

        # Insert score breakdown if given
        if scores:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "Score Breakdown:", ln=True)
            pdf.set_font("Arial", size=11)
            for k, v in scores.items():
                if k == 'Total':
                    continue
                pdf.cell(0, 8, f"- {k}: {v}/20", ln=True)
            pdf.ln(6)

        pdf.set_font("Arial", size=11)
        # Keep original behavior of encoding to latin-1 and dropping unsupported chars
        pdf.multi_cell(0, 8, txt=content.encode('latin-1', 'ignore').decode('latin-1'))
        return pdf.output(dest='S').encode('latin-1')

    # ReportLab path (Unicode-friendly)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, leading=18)
    story.append(Paragraph("MANUSCRIPT ASSESSMENT REPORT", title_style))

    subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)
    header = "Standard: Scopus/Web of Science Q1 Quality"
    if user_name:
        header = f"Prepared for: {user_name} | {header}"
    story.append(Paragraph(header, subtitle_style))
    story.append(Spacer(1, 8))

    if scores:
        story.append(Paragraph("Score Breakdown:", styles['Heading3']))
        for k, v in scores.items():
            if k == 'Total':
                continue
            story.append(Paragraph(f"- {k}: {v}/20", styles['Normal']))
        story.append(Spacer(1, 6))

    # Add main content (allowing multiple paragraphs)
    # We keep it simple: treat as one long paragraph; large documents could be handled
    # more gracefully in the future.
    story.append(Paragraph(content.replace('\n', '<br/>'), styles['Normal']))

    doc.build(story)
    return buffer.getvalue()
