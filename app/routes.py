"""
FastAPI Route Handlers for ComicCraft
"""
import logging
import os
from typing import Optional
from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.models.schemas import ComicRequest
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_panel_images, generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

STATIC_PANELS_DIR = "static/panels"
STATIC_EXPORTS_DIR = "static/exports"
DEFAULT_PDF_PATH = os.path.join(STATIC_EXPORTS_DIR, "comic_story.pdf")
DEFAULT_COMIC_IMG_PATH = os.path.join(STATIC_EXPORTS_DIR, "final_comic.png")


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Render the main comic story creation form."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "art_styles": ["Manga", "Anime", "American", "Belgian"],
            "tones": ["Funny", "Adventure", "Dramatic", "Inspirational", "Mystery"],
        }
    )


@router.post("/generate", response_class=HTMLResponse)
async def post_generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    """
    Execute the end-to-end comic generation pipeline:
    User Input -> Gemini Flash -> Gemini Pro -> Stable Diffusion -> Layout Builder -> PDF
    """
    # 1. Validate Form Input
    try:
        req = ComicRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )
    except Exception as exc:
        logger.warning("Input validation error: %s", exc)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Invalid form input: {exc}",
                "form_data": {
                    "story_prompt": story_prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                },
                "art_styles": ["Manga", "Anime", "American", "Belgian"],
                "tones": ["Funny", "Adventure", "Dramatic", "Inspirational", "Mystery"],
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 2. Stage 1: Gemini Flash (5-panel structured outline)
        logger.info("Stage 1: Generating 5-panel outline with Gemini Flash...")
        outline_response = generate_outline(
            story_prompt=req.story_prompt,
            character_name=req.character_name,
            setting=req.setting,
            tone=req.tone,
            art_style=req.art_style
        )

        # 3. Stage 2: Gemini Pro (Rich story, narration, dialogue & refined prompts)
        logger.info("Stage 2: Expanding story with Gemini Pro...")
        story_response = generate_story(
            outline=outline_response,
            story_prompt=req.story_prompt,
            character_name=req.character_name,
            setting=req.setting,
            tone=req.tone,
            art_style=req.art_style
        )

        # 4. Stage 3: Stable Diffusion (Generate 5 panel illustrations)
        logger.info("Stage 3: Generating panel illustrations via Stable Diffusion...")
        panel_dicts = [p.model_dump() for p in story_response.panels]
        image_paths = generate_panel_images(
            panels=panel_dicts,
            art_style=req.art_style,
            output_dir=STATIC_PANELS_DIR
        )

        # 5. Stage 4: Layout Builder (Composite 5 panels with captions)
        logger.info("Stage 4: Compositing 5-panel comic strip...")
        comic_image_path = build_comic_layout(
            panels=story_response.panels,
            image_paths=image_paths,
            output_path=DEFAULT_COMIC_IMG_PATH
        )

        # 6. Stage 5: PDF Export (Build downloadable A4 PDF)
        logger.info("Stage 5: Building PDF document...")
        pdf_path = save_pdf(
            comic_image_path=comic_image_path,
            pdf_path=DEFAULT_PDF_PATH
        )

        # Relative paths for frontend rendering
        panel_urls = [f"/static/panels/panel_{i}.png" for i in range(1, 6)]
        comic_url = "/static/exports/final_comic.png"
        pdf_url = "/download-pdf"

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "story_prompt": req.story_prompt,
                "character_name": req.character_name,
                "setting": req.setting,
                "tone": req.tone,
                "art_style": req.art_style,
                "panels": story_response.panels,
                "panel_urls": panel_urls,
                "comic_image_url": comic_url,
                "pdf_url": pdf_url,
            }
        )

    except Exception as exc:
        logger.error("Pipeline execution failed: %s", exc, exc_info=True)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Comic Generation Failed: {str(exc)}",
                "form_data": {
                    "story_prompt": req.story_prompt,
                    "character_name": req.character_name,
                    "setting": req.setting,
                    "tone": req.tone,
                    "art_style": req.art_style,
                },
                "art_styles": ["Manga", "Anime", "American", "Belgian"],
                "tones": ["Funny", "Adventure", "Dramatic", "Inspirational", "Mystery"],
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/download-pdf")
async def download_pdf():
    """Download the generated comic strip as a PDF file."""
    if not os.path.exists(DEFAULT_PDF_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No generated PDF found. Please generate a comic strip first."
        )
    return FileResponse(
        path=DEFAULT_PDF_PATH,
        media_type="application/pdf",
        filename="comic_craft_story.pdf",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    """Render the PDF export confirmation and download info page."""
    pdf_exists = os.path.exists(DEFAULT_PDF_PATH)
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_exists": pdf_exists,
            "pdf_url": "/download-pdf" if pdf_exists else None
        }
    )


@router.get("/test-image")
async def test_image():
    """Development test route to verify image synthesizer / pipeline operation."""
    test_path = os.path.join(STATIC_PANELS_DIR, "test_sample.png")
    saved = generate_image(
        prompt="A heroic cyberpunk warrior overlooking a neon city",
        output_path=test_path,
        art_style="Anime",
        panel_number=1
    )
    return {
        "status": "success",
        "message": "Image generated successfully",
        "path": saved,
        "url": "/static/panels/test_sample.png"
    }
