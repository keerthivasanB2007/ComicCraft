"""
Gemini Flash Service - Generates structured 5-panel comic outlines using Google GenAI SDK.
"""
import json
import logging
import os
import re
from typing import Optional

from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types

from app.models.schemas import OutlineResponse

# Load environment variables
load_dotenv(find_dotenv(usecwd=True), override=True)

logger = logging.getLogger(__name__)

FLASH_MODEL_NAME = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.7-flash")


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


OUTLINE_SYSTEM_PROMPT = """
You are an expert comic storyboard writer.
Create a structured 5-panel comic outline based on the user's story prompt, character, setting, tone, and art style.

Return ONLY a valid JSON object with the following structure:
{
  "panels": [
    {
      "panel_number": 1,
      "title": "Short title describing panel 1",
      "scene_description": "Clear visual description of characters, actions, and background",
      "image_prompt": "Prompt for text-to-image generator describing visual elements, lighting, and composition"
    },
    {
      "panel_number": 2,
      "title": "Short title describing panel 2",
      "scene_description": "Clear visual description of characters, actions, and background",
      "image_prompt": "Prompt for text-to-image generator describing visual elements, lighting, and composition"
    },
    {
      "panel_number": 3,
      "title": "Short title describing panel 3",
      "scene_description": "Clear visual description of characters, actions, and background",
      "image_prompt": "Prompt for text-to-image generator describing visual elements, lighting, and composition"
    },
    {
      "panel_number": 4,
      "title": "Short title describing panel 4",
      "scene_description": "Clear visual description of characters, actions, and background",
      "image_prompt": "Prompt for text-to-image generator describing visual elements, lighting, and composition"
    },
    {
      "panel_number": 5,
      "title": "Short title describing panel 5",
      "scene_description": "Clear visual description of characters, actions, and background",
      "image_prompt": "Prompt for text-to-image generator describing visual elements, lighting, and composition"
    }
  ]
}

STRICT REQUIREMENTS:
- Exactly 5 panels numbered 1 to 5.
- Do not output markdown backticks or commentary outside the JSON.
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


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    model_name: Optional[str] = None,
) -> OutlineResponse:
    """
    Generate a 5-panel comic outline using Gemini Flash.
    """
    client = get_client()
    target_model = model_name or FLASH_MODEL_NAME

    user_content = f"""
Story Prompt: {story_prompt}
Main Character: {character_name}
Setting: {setting}
Tone: {tone}
Art Style: {art_style}

Generate a compelling 5-panel comic outline following the requested JSON schema.
"""

    logger.info("Calling Gemini Flash (%s) for outline generation...", target_model)
    
    # Candidate models for fallback if quota or model unavailable
    models_to_try = [target_model]
    for fallback in ["gemini-3.7-flash", "gemini-flash-latest", "gemini-3.6-flash", "gemini-3-flash-preview"]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error = None
    for model_id in models_to_try:
        try:
            config = types.GenerateContentConfig(
                system_instruction=OUTLINE_SYSTEM_PROMPT,
                response_mime_type="application/json"
            )
            response = client.models.generate_content(
                model=model_id,
                contents=user_content,
                config=config
            )
            if response and response.text:
                parsed_json = clean_json_response(response.text)
                return OutlineResponse.model_validate(parsed_json)
        except Exception as exc:
            logger.warning("Gemini Flash attempt with %s failed: %s", model_id, exc)
            last_error = exc

    raise ValueError(f"Gemini Flash outline generation failed across models: {last_error}")
