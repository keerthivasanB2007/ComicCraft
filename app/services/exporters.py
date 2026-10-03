"""
Exporters Service - PDF generation using ReportLab.
"""
import logging
import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)


def save_pdf(comic_image_path: str, pdf_path: str = "static/exports/comic_story.pdf") -> str:
    """
    Generate a high-quality A4 PDF document embedding the generated comic strip.
    Accurately computes available page dimensions to ensure the entire comic and title
    fit on a single page without creating unwanted page breaks.
    """
    if not os.path.exists(comic_image_path):
        raise FileNotFoundError(f"Comic image not found at: {comic_image_path}")

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # A4 Page Dimensions (595.27 x 841.89 points)
    a4_width, a4_height = A4
    margin = 15
    top_margin = 15
    bottom_margin = 15
    header_space = 32  # space reserved for title, leading, and padding

    max_w = a4_width - (2 * margin)
    max_h = a4_height - (top_margin + bottom_margin) - header_space

    with Image.open(comic_image_path) as img:
        orig_w, orig_h = img.size

    aspect = orig_h / float(orig_w)
    target_w = max_w
    target_h = target_w * aspect

    # Strict constraint to prevent pushing image to Page 2
    if target_h > max_h:
        target_h = max_h
        target_w = target_h / aspect

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=16,
        alignment=1,  # Centered
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    elements = [
        Paragraph("<b>ComicCraft AI Story</b>", title_style),
        RLImage(comic_image_path, width=target_w, height=target_h)
    ]

    doc.build(elements)
    logger.info("Exported single-page PDF successfully to %s", pdf_path)
    return pdf_path
