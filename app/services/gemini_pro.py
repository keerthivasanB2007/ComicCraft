"""
Gemini Pro Service - Expands 5-panel outline into rich story, narration, dialogue, and refined visual prompts using Google GenAI SDK.
"""
import json
import logging
import os
import re
from typing import Optional

from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types

from app.models.schemas import OutlineResponse, StoryResponse

# Load environment variables
load_dotenv(find_dotenv(usecwd=True), override=True)

logger = logging.getLogger(__name__)

PRO_MODEL_NAME = os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")


def get_api_key() -> str:
    """Retrieve Gemini API Key from environment variables."""
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip() or (os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Please set GEMINI_API_KEY in your .env file."
        )
    return api_key


def get_client() -> genai.Client:
    """Initialize and return Google GenAI Client."""
    api_key = get_api_key()
    return genai.Client(api_key=api_key)


STORY_SYSTEM_PROMPT = """
You are a master comic book scriptwriter and visual director.
You will receive a 5-panel outline for a comic along with the user's story parameters.
Your job is to expand this into a detailed comic script with impactful narration, punchy character dialogue, and highly descriptive text-to-image prompts tailored for Stable Diffusion.

Return ONLY a valid JSON object with the following structure:
{
  "panels": [
    {
      "panel_number": 1,
      "title": "Panel Title",
      "narration": "Engaging scene caption or narration for the panel",
      "dialogue": "Character Name: Dialogue line (or empty string if none)",
      "image_prompt": "Highly detailed Stable Diffusion prompt describing subject, composition, background, lighting, and art style details (no speech bubbles, no text)"
    },
    {
      "panel_number": 2,
      "title": "Panel Title",
      "narration": "Engaging scene caption or narration for the panel",
      "dialogue": "Character Name: Dialogue line (or empty string if none)",
      "image_prompt": "Highly detailed Stable Diffusion prompt describing subject, composition, background, lighting, and art style details (no speech bubbles, no text)"
    },
    {
      "panel_number": 3,
      "title": "Panel Title",
      "narration": "Engaging scene caption or narration for the panel",
      "dialogue": "Character Name: Dialogue line (or empty string if none)",
      "image_prompt": "Highly detailed Stable Diffusion prompt describing subject, composition, background, lighting, and art style details (no speech bubbles, no text)"
    },
    {
      "panel_number": 4,
      "title": "Panel Title",
      "narration": "Engaging scene caption or narration for the panel",
      "dialogue": "Character Name: Dialogue line (or empty string if none)",
      "image_prompt": "Highly detailed Stable Diffusion prompt describing subject, composition, background, lighting, and art style details (no speech bubbles, no text)"
    },
    {
      "panel_number": 5,
      "title": "Panel Title",
      "narration": "Engaging scene caption or narration for the panel",
      "dialogue": "Character Name: Dialogue line (or empty string if none)",
      "image_prompt": "Highly detailed Stable Diffusion prompt describing subject, composition, background, lighting, and art style details (no speech bubbles, no text)"
    }
  ]
}

STRICT REQUIREMENTS:
- Exactly 5 panels numbered 1 to 5.
- Narration and dialogue must be compelling, clear, and well-written.
- Image prompts must NEVER include speech bubbles, text overlays, or watermarks.
- Return ONLY valid JSON.
"""


def clean_json_response(raw_text: str) -> dict:
    """Extract and parse JSON from the model response."""
    text = raw_text.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1:
        text = text[first_brace:last_brace + 1]

    return json.loads(text)


def generate_story(
    outline: OutlineResponse,
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    model_name: Optional[str] = None,
) -> StoryResponse:
    """
    Expand a 5-panel outline into rich story, narration, and dialogue using Gemini Pro.
    """
    client = get_client()
    target_model = model_name or PRO_MODEL_NAME

    outline_payload = outline.model_dump()

    user_content = f"""
Original Story Prompt: {story_prompt}
Main Character: {character_name}
Setting: {setting}
Tone: {tone}
Art Style: {art_style}

Gemini Flash 5-Panel Outline:
{json.dumps(outline_payload, indent=2)}

Please expand this outline into the final detailed 5-panel comic script adhering to the JSON schema.
"""

    logger.info("Calling Gemini Pro (%s) for story expansion...", target_model)

    models_to_try = [target_model]
    for fallback in [
        "gemini-pro-latest",
        "gemini-3-flash-preview",
        "gemini-3.7-flash",
        "gemini-flash-latest",
        "gemini-3.1-flash-lite",
        "gemini-3.6-flash"
    ]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error = None
    for model_id in models_to_try:
        try:
            config = types.GenerateContentConfig(
                system_instruction=STORY_SYSTEM_PROMPT,
                response_mime_type="application/json"
            )
            response = client.models.generate_content(
                model=model_id,
                contents=user_content,
                config=config
            )
            if response and response.text:
                parsed_json = clean_json_response(response.text)
                return StoryResponse.model_validate(parsed_json)
        except Exception as exc:
            logger.warning("Gemini Pro attempt with %s failed: %s", model_id, exc)
            last_error = exc

    raise ValueError(f"Gemini Pro story generation failed across models: {last_error}")
