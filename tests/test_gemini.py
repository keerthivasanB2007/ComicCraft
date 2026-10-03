"""
Unit tests for Gemini Flash and Gemini Pro services with mocked responses.
"""
import json
from unittest.mock import patch, MagicMock
import pytest
from app.services.gemini_flash import generate_outline, clean_json_response
from app.services.gemini_pro import generate_story
from app.models.schemas import OutlineResponse, PanelOutline


def test_clean_json_response():
    """Test extracting JSON from markdown-fenced content."""
    raw_markdown = """```json
    {
      "panels": [
        {"panel_number": 1, "title": "Intro", "scene_description": "A dark street", "image_prompt": "Street at night"},
        {"panel_number": 2, "title": "Action", "scene_description": "Hero jumps", "image_prompt": "Hero in air"},
        {"panel_number": 3, "title": "Conflict", "scene_description": "Villain appears", "image_prompt": "Villain grin"},
        {"panel_number": 4, "title": "Climax", "scene_description": "Battle begins", "image_prompt": "Sparks fly"},
        {"panel_number": 5, "title": "End", "scene_description": "Victory", "image_prompt": "Sunrise"}
      ]
    }
    ```"""
    parsed = clean_json_response(raw_markdown)
    assert "panels" in parsed
    assert len(parsed["panels"]) == 5


@patch("app.services.gemini_flash.get_client")
def test_generate_outline_mocked(mock_get_client):
    """Test Gemini Flash outline generation with mocked Google GenAI client."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "panels": [
            {"panel_number": i, "title": f"Title {i}", "scene_description": f"Scene {i}", "image_prompt": f"Prompt {i}"}
            for i in range(1, 6)
        ]
    })
    mock_client.models.generate_content.return_value = mock_response

    outline = generate_outline(
        story_prompt="Space exploration journey",
        character_name="Nova",
        setting="Jupiter Orbit",
        tone="Inspirational",
        art_style="American"
    )

    assert isinstance(outline, OutlineResponse)
    assert len(outline.panels) == 5
    assert outline.panels[0].panel_number == 1
    assert outline.panels[0].title == "Title 1"


@patch("app.services.gemini_pro.get_client")
def test_generate_story_mocked(mock_get_client):
    """Test Gemini Pro story generation with mocked Google GenAI client."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "panels": [
            {
                "panel_number": i,
                "title": f"Story Title {i}",
                "narration": f"Narration for panel {i}",
                "dialogue": f"Nova: We did it in panel {i}!",
                "image_prompt": f"SD prompt for panel {i}"
            }
            for i in range(1, 6)
        ]
    })
    mock_client.models.generate_content.return_value = mock_response

    mock_outline = OutlineResponse(
        panels=[
            PanelOutline(
                panel_number=i,
                title=f"Title {i}",
                scene_description=f"Scene {i}",
                image_prompt=f"Prompt {i}"
            )
            for i in range(1, 6)
        ]
    )

    story = generate_story(
        outline=mock_outline,
        story_prompt="Space exploration journey",
        character_name="Nova",
        setting="Jupiter Orbit",
        tone="Inspirational",
        art_style="American"
    )

    assert len(story.panels) == 5
    assert "Nova:" in story.panels[0].dialogue
