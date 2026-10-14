import io
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from fpdf import FPDF
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from pptx.dml.color import RGBColor as PptxRGBColor


def clean_markdown(text: str) -> str:
    """Removes markdown symbols for plain-text formatting in docs/pptx/pdf."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"#{1,6}\s?", "", text)
    return text.strip()


# -------------------------------------------------------------
# 1. WORD DOCUMENT GENERATOR (All details shown on site)
# -------------------------------------------------------------
def generate_word_document(topic: str, report: str, research_notes: str, analysis: str, sources: list) -> bytes:
    doc = Document()

    # Document Header
    title = doc.add_heading("Comprehensive Research Briefing", level=0)
    title.runs[0].font.color.rgb = RGBColor(20, 50, 90)

    p_topic = doc.add_paragraph()
    p_topic.add_run("Research Topic: ").bold = True
    p_topic.add_run(topic)
    doc.add_paragraph()

    # Section 1: Final Report
    doc.add_heading("1. Executive Research Report", level=1)
    doc.add_paragraph(clean_markdown(report))
    doc.add_paragraph()

    # Section 2: Analyst Insights
    doc.add_heading("2. Research Analyst's Insights", level=1)
    doc.add_paragraph(clean_markdown(analysis))
    doc.add_paragraph()

    # Section 3: Research Findings / Scout Notes
    doc.add_heading("3. Raw Research Findings & Evidence", level=1)
    doc.add_paragraph(clean_markdown(research_notes))
    doc.add_paragraph()

    # Section 4: Sources
    doc.add_heading("4. Verified Sources", level=1)
    for item in sources:
        title_text = item.get("title", "Source")
        link_text = item.get("link", "")
        doc.add_paragraph(f"[{item.get('id', '-')}] {title_text} — {link_text}", style="List Bullet")

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# -------------------------------------------------------------
# 2. POWERPOINT PRESENTATION GENERATOR (.pptx)
# -------------------------------------------------------------
def generate_pptx_deck(topic: str, report: str, analysis: str, sources: list) -> bytes:
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)

    blank_layout = prs.slide_layouts[6]

    def add_custom_slide(title_text: str, content_bullet_points: list):
        slide = prs.slides.add_slide(blank_layout)

        # Slide Title
        title_box = slide.shapes.add_textbox(PptxInches(1.0), PptxInches(0.8), PptxInches(11.33), PptxInches(1.0))
        tf_title = title_box.text_frame
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.bold = True
        p_title.font.size = PptxPt(32)
        p_title.font.color.rgb = PptxRGBColor(24, 43, 73)

        # Slide Content Box
        body_box = slide.shapes.add_textbox(PptxInches(1.0), PptxInches(2.0), PptxInches(11.33), PptxInches(4.8))
        tf_body = body_box.text_frame
        tf_body.word_wrap = True

        for i, point in enumerate(content_bullet_points):
            p = tf_body.paragraphs[0] if i == 0 else tf_body.add_paragraph()
            p.text = f"• {point.strip()}"
            p.font.size = PptxPt(18)
            p.font.color.rgb = PptxRGBColor(50, 50, 50)
            p.space_after = PptxPt(14)

    # Slide 1: Title Slide
    title_slide = prs.slides.add_slide(blank_layout)
    box = title_slide.shapes.add_textbox(PptxInches(1.5), PptxInches(2.4), PptxInches(10.3), PptxInches(2.5))
    tf = box.text_frame
    p1 = tf.paragraphs[0]
    p1.text = "Executive Research Briefing"
    p1.font.bold = True
    p1.font.size = PptxPt(40)
    p1.font.color.rgb = PptxRGBColor(24, 43, 73)

    p2 = tf.add_paragraph()
    p2.text = f"Topic: {topic}"
    p2.font.size = PptxPt(22)
    p2.font.color.rgb = PptxRGBColor(100, 100, 100)
    p2.space_before = PptxPt(20)

    # Chunk clean texts into bullet points
    def extract_bullets(text: str, max_points: int = 4):
        cleaned = clean_markdown(text)
        lines = [line.strip() for line in cleaned.split("\n") if len(line.strip()) > 25]
        return lines[:max_points] if lines else [cleaned[:300]]

    # Slide 2: Executive Summary & Core Insights
    add_custom_slide("Executive Summary & Core Takeaways", extract_bullets(report, 4))

    # Slide 3: Analyst Evaluation & Trends
    add_custom_slide("Strategic Insights & Trends", extract_bullets(analysis, 4))

    # Slide 4: Citations & Evidence
    source_lines = [
        f"{item.get('title', 'Source')} ({item.get('link', '')})"
        for item in sources[:4]
    ]
    add_custom_slide("Key Sources & References", source_lines if source_lines else ["Live Web Search Analysis"])

    buffer = io.BytesIO()
    prs.save(buffer)
    return buffer.getvalue()


# -------------------------------------------------------------
# 3. EXECUTIVE BRIEFING PDF GENERATOR (.pdf)
# -------------------------------------------------------------
def generate_pdf_report(topic: str, report: str, analysis: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 10, "Executive Research Presentation Report", ln=True)

    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(100, 100, 100)
    topic_sanitized = topic.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 8, f"Topic: {topic_sanitized}", ln=True)
    pdf.ln(4)

    # Separator
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Section 1
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 8, "1. Executive Briefing", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    clean_rep = clean_markdown(report).encode("latin-1", "replace").decode("latin-1")
    for line in clean_rep.split("\n"):
        if line.strip():
            pdf.multi_cell(0, 5, line.strip())
            pdf.ln(2)

    pdf.ln(4)

    # Section 2
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 8, "2. Strategic Analyst Evaluation", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    clean_an = clean_markdown(analysis).encode("latin-1", "replace").decode("latin-1")
    for line in clean_an.split("\n"):
        if line.strip():
            pdf.multi_cell(0, 5, line.strip())
            pdf.ln(2)

    return bytes(pdf.output())