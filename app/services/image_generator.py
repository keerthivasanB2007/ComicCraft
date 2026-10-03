"""
Image Generation Service using Stable Diffusion / Hugging Face Diffusers.
"""
import logging
import os
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Style mappings for Stable Diffusion prompt enhancement
STYLE_PROMPTS = {
    "Manga": "manga masterpiece, high-contrast black and white ink sketch, sharp clean lines, dramatic screentone shading, manga panel art",
    "Anime": "high quality anime artwork, vibrant colors, smooth cel shading, expressive eyes, dynamic composition, Makoto Shinkai aesthetic",
    "American": "classic American comic book style, bold black inking, saturated colors, dynamic heroic framing, Marvel and DC comic aesthetic",
    "Belgian": "Franco-Belgian comic art, ligne claire style, clean outlines, flat gouache colors, Herge Tintin comic book illustration",
}

NEGATIVE_PROMPT = (
    "speech bubbles, text, dialogue, letters, watermark, signature, logo, "
    "blurry, distorted, bad anatomy, extra limbs, poorly drawn hands, low resolution"
)

# Global pipeline cache
_SD_PIPELINE = None


def get_pipeline():
    """
    Lazy loader and singleton cache for the Stable Diffusion pipeline.
    Uses Hugging Face Diffusers with local cache support.
    """
    global _SD_PIPELINE
    if _SD_PIPELINE is not None:
        return _SD_PIPELINE

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        # Default to compact, fast Stable Diffusion model compatible with CPU/GPU
        model_id = os.getenv("SD_MODEL_ID", "segmind/tiny-sd")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        logger.info("Initializing Stable Diffusion pipeline (%s) on %s...", model_id, device)

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            safety_checker=None
        )
        pipe = pipe.to(device)

        if device == "cuda":
            pipe.enable_attention_slicing()

        _SD_PIPELINE = pipe
        logger.info("Stable Diffusion pipeline initialized successfully on %s.", device)
        return _SD_PIPELINE

    except Exception as exc:
        logger.warning(
            "Stable Diffusion pipeline could not be initialized (%s). "
            "Will fall back to synthesizer.", exc
        )
        return None


def generate_fallback_image(prompt: str, art_style: str, panel_number: int, output_path: str, width: int = 512, height: int = 512) -> str:
    """
    Development fallback placeholder generator when PyTorch/Diffusers dependencies fail.
    """
    style_palettes = {
        "Manga": [(245, 245, 245), (30, 30, 30)],
        "Anime": [(255, 225, 230), (70, 40, 120)],
        "American": [(255, 240, 200), (180, 20, 20)],
        "Belgian": [(220, 240, 255), (20, 90, 160)],
    }
    bg_color, accent_color = style_palettes.get(art_style, [(240, 240, 240), (50, 50, 50)])

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    border = 12
    draw.rectangle(
        [(border, border), (width - border, height - border)],
        outline=accent_color,
        width=4
    )

    banner_height = 50
    draw.rectangle(
        [(border, border), (width - border, border + banner_height)],
        fill=accent_color
    )

    try:
        font_large = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    header_text = f"PANEL {panel_number} • {art_style.upper()} STYLE"
    draw.text((border + 15, border + 14), header_text, fill="white", font=font_large)

    words = prompt.split()
    lines = []
    curr = ""
    for w in words:
        test = f"{curr} {w}".strip()
        if len(test) < 45:
            curr = test
        else:
            lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)

    y_offset = height // 2 - (len(lines) * 20) // 2
    for line in lines[:8]:
        draw.text((border + 25, y_offset), line, fill=accent_color, font=font_small)
        y_offset += 22

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, format="PNG")
    logger.info("Saved fallback placeholder panel %d to %s", panel_number, output_path)
    return output_path


def generate_image(
    prompt: str,
    output_path: str,
    art_style: str = "Anime",
    panel_number: int = 1,
    width: int = 512,
    height: int = 512,
    num_inference_steps: Optional[int] = None,
) -> str:
    """
    Generate an actual comic illustration using Stable Diffusion.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pipe = get_pipeline()

    style_suffix = STYLE_PROMPTS.get(art_style, STYLE_PROMPTS["Anime"])
    full_prompt = f"{prompt}, {style_suffix}, high detail, masterpiece"

    if pipe is not None:
        try:
            steps = num_inference_steps or int(os.getenv("SD_STEPS", "10"))
            logger.info("Generating panel %d with Stable Diffusion (%d steps)...", panel_number, steps)
            result = pipe(
                prompt=full_prompt,
                negative_prompt=NEGATIVE_PROMPT,
                width=width,
                height=height,
                num_inference_steps=steps,
            )
            image = result.images[0]
            image.save(output_path)
            logger.info("Stable Diffusion illustration saved successfully to %s", output_path)
            return output_path
        except Exception as exc:
            logger.error("Error during Stable Diffusion inference: %s", exc)

    # Fallback placeholder if pipeline unavailable
    return generate_fallback_image(
        prompt=prompt,
        art_style=art_style,
        panel_number=panel_number,
        output_path=output_path,
        width=width,
        height=height
    )


def generate_panel_images(
    panels: List[dict],
    art_style: str,
    output_dir: str = "static/panels"
) -> List[str]:
    """
    Generate illustrations for all 5 comic panels.
    Returns list of saved file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []

    for i, panel in enumerate(panels, start=1):
        prompt = panel.get("image_prompt") or panel.get("scene_description", f"Comic scene {i}")
        file_name = f"panel_{i}.png"
        output_path = os.path.join(output_dir, file_name)

        saved_path = generate_image(
            prompt=prompt,
            output_path=output_path,
            art_style=art_style,
            panel_number=i
        )
        image_paths.append(saved_path)

    return image_paths
