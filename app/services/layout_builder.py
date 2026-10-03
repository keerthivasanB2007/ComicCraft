"""
Layout Builder Service - Composites 5 panels into a structured comic strip.
"""
import logging
import os
from typing import List, Union
from PIL import Image, ImageDraw, ImageFont

from app.models.schemas import PanelStory

logger = logging.getLogger(__name__)

BORDER_THICKNESS = 6
CAPTION_BOX_BORDER = 3
OUTLINE_THICKNESS = 2
DEFAULT_FONT_SIZE = 19
HEADER_FONT_SIZE = 22
SMALL_FONT_SIZE = 16


def load_font(size: int) -> ImageFont.ImageFont:
    """Load Arial TrueType font or fallback to PIL default."""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()


def add_border(image: Image.Image, border_thickness: int = BORDER_THICKNESS, color: str = "black") -> Image.Image:
    """Add a bold border around an image."""
    bordered = Image.new(
        "RGB",
        (image.width + 2 * border_thickness, image.height + 2 * border_thickness),
        color
    )
    bordered.paste(image, (border_thickness, border_thickness))
    return bordered


def wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    """Wraps text into multiple lines based on maximum pixel width."""
    if not text:
        return []

    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def draw_text_with_outline(
    draw: ImageDraw.Draw,
    position: tuple,
    text: str,
    font: ImageFont.ImageFont,
    fill_color: str = "black",
    outline_color: str = "white",
    outline_thickness: int = OUTLINE_THICKNESS
):
    """Draws text with a visible outline for readability."""
    x, y = position
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=fill_color)


def decorate_panel(
    panel_img: Image.Image,
    panel_number: int,
    title: str,
    narration: str,
    dialogue: str,
    target_width: int = 600,
    target_height: int = 500
) -> Image.Image:
    """
    Renders header banner, wrapped narration box, panel artwork, and dialogue caption box.
    """
    inner_width = target_width - (2 * BORDER_THICKNESS)
    header_height = 36
    narration_height = 54
    dialogue_height = 56
    inner_art_height = target_height - header_height - narration_height - dialogue_height

    art_resized = panel_img.resize((inner_width, inner_art_height), Image.Resampling.LANCZOS)

    panel_canvas = Image.new("RGB", (target_width, target_height), "white")
    draw = ImageDraw.Draw(panel_canvas)

    font_header = load_font(HEADER_FONT_SIZE)
    font_body = load_font(DEFAULT_FONT_SIZE)
    font_small = load_font(SMALL_FONT_SIZE)

    # 1. Header Banner (Panel Number & Title)
    draw.rectangle([(0, 0), (target_width, header_height)], fill="#1E293B")
    header_text = f"Panel {panel_number}: {title}"
    draw.text((15, 6), header_text, fill="white", font=font_header)

    # 2. Narration Box (Yellow caption box with multiline wrapping)
    draw.rectangle(
        [(0, header_height), (target_width, header_height + narration_height)],
        fill="#FEF3C7",
        outline="#B45309",
        width=1
    )

    max_narr_w = target_width - 30
    narr_lines = wrap_text(draw, narration or "...", font_small, max_narr_w)
    curr_narr_y = header_height + 6
    for nline in narr_lines[:2]:
        draw.text((15, curr_narr_y), nline, fill="#92400E", font=font_small)
        curr_narr_y += 21

    # 3. Paste Artwork
    art_y = header_height + narration_height
    panel_canvas.paste(art_resized, (BORDER_THICKNESS, art_y))

    # 4. Dialogue Box at Bottom
    dialogue_y = art_y + inner_art_height
    draw.rectangle(
        [(0, dialogue_y), (target_width, target_height)],
        fill="#F8FAFC",
        outline="#0F172A",
        width=2
    )

    diag_lines = wrap_text(draw, dialogue or "(No dialogue)", font_body, target_width - 30)
    curr_diag_y = dialogue_y + 6
    for dline in diag_lines[:2]:
        bbox = draw.textbbox((0, 0), dline, font=font_body)
        text_w = bbox[2] - bbox[0]
        text_x = (target_width - text_w) // 2
        draw_text_with_outline(draw, (text_x, curr_diag_y), dline, font_body, fill_color="#0F172A", outline_color="#E2E8F0")
        curr_diag_y += 22

    # 5. Outer Border
    return add_border(panel_canvas, BORDER_THICKNESS, color="#0F172A")


def build_comic_layout(
    panels: List[Union[PanelStory, dict]],
    image_paths: List[str],
    output_path: str = "static/exports/final_comic.png"
) -> str:
    """
    Composites exactly 5 panels into a 5-panel layout:
    Row 1: Panel 1, Panel 2
    Row 2: Panel 3, Panel 4
    Row 3: Panel 5 (Wide Climax Panel)
    """
    if len(image_paths) != 5:
        raise ValueError(f"Layout builder requires exactly 5 panel images, got {len(image_paths)}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    panel_w = 600
    panel_h = 520

    decorated_panels = []
    for i in range(5):
        p_data = panels[i]
        if isinstance(p_data, PanelStory):
            p_dict = p_data.model_dump()
        else:
            p_dict = p_data

        panel_num = p_dict.get("panel_number", i + 1)
        title = p_dict.get("title", f"Scene {panel_num}")
        narration = p_dict.get("narration", "")
        dialogue = p_dict.get("dialogue", "")

        raw_img = Image.open(image_paths[i])
        dec_panel = decorate_panel(
            raw_img,
            panel_number=panel_num,
            title=title,
            narration=narration,
            dialogue=dialogue,
            target_width=panel_w,
            target_height=panel_h
        )
        decorated_panels.append(dec_panel)

    single_panel_w, single_panel_h = decorated_panels[0].size
    margin = 20
    header_title_height = 80

    total_width = (single_panel_w * 2) + (margin * 3)
    total_height = header_title_height + (single_panel_h * 3) + (margin * 4)

    # Master Canvas
    comic_canvas = Image.new("RGB", (total_width, total_height), "#0F172A")
    draw = ImageDraw.Draw(comic_canvas)

    # Clean Comic Strip Banner Title without unsupported special characters
    font_main = load_font(34)
    comic_title = "COMICCRAFT • AI COMIC STRIP"
    bbox = draw.textbbox((0, 0), comic_title, font=font_main)
    title_w = bbox[2] - bbox[0]
    draw.text(((total_width - title_w) // 2, 24), comic_title, fill="#F8FAFC", font=font_main)

    # Row 1: Panels 1 & 2
    y_row1 = header_title_height + margin
    comic_canvas.paste(decorated_panels[0], (margin, y_row1))
    comic_canvas.paste(decorated_panels[1], (margin * 2 + single_panel_w, y_row1))

    # Row 2: Panels 3 & 4
    y_row2 = y_row1 + single_panel_h + margin
    comic_canvas.paste(decorated_panels[2], (margin, y_row2))
    comic_canvas.paste(decorated_panels[3], (margin * 2 + single_panel_w, y_row2))

    # Row 3: Panel 5 (Centered climax panel)
    y_row3 = y_row2 + single_panel_h + margin
    x_panel5 = (total_width - single_panel_w) // 2
    comic_canvas.paste(decorated_panels[4], (x_panel5, y_row3))

    comic_canvas.save(output_path, format="PNG")
    logger.info("Final 5-panel comic strip saved to %s", output_path)
    return output_path
