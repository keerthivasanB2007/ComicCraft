"""
Unit tests for Pydantic data schemas.
"""
import pytest
from pydantic import ValidationError
from app.models.schemas import (
    ComicRequest,
    PanelOutline,
    OutlineResponse,
    PanelStory,
    StoryResponse,
)


def test_comic_request_valid():
    """Test valid ComicRequest instantiations."""
    req = ComicRequest(
        story_prompt="A hero saves the city from robots",
        character_name="Volt",
        setting="Cyber City",
        tone="Dramatic",
        art_style="Anime"
    )
    assert req.story_prompt == "A hero saves the city from robots"
    assert req.character_name == "Volt"
    assert req.setting == "Cyber City"
    assert req.tone == "Dramatic"
    assert req.art_style == "Anime"


def test_comic_request_empty_fields():
    """Test that blank/empty fields raise ValidationError."""
    with pytest.raises(ValidationError):
        ComicRequest(
            story_prompt="   ",
            character_name="Volt",
            setting="City",
            tone="Funny",
            art_style="Manga"
        )


def test_outline_response_five_panels_valid():
    """Test OutlineResponse validates exactly 5 panels."""
    panels = [
        PanelOutline(
            panel_number=i,
            title=f"Scene {i}",
            scene_description=f"Description for panel {i}",
            image_prompt=f"Prompt for panel {i}"
        )
        for i in range(1, 6)
    ]
    outline = OutlineResponse(panels=panels)
    assert len(outline.panels) == 5


def test_outline_response_invalid_panel_count():
    """Test OutlineResponse rejects non-5 panel count."""
    panels = [
        PanelOutline(
            panel_number=i,
            title=f"Scene {i}",
            scene_description=f"Description for panel {i}",
            image_prompt=f"Prompt for panel {i}"
        )
        for i in range(1, 4)  # Only 3 panels
    ]
    with pytest.raises(ValidationError):
        OutlineResponse(panels=panels)


def test_story_response_five_panels_valid():
    """Test StoryResponse validates exactly 5 panels."""
    panels = [
        PanelStory(
            panel_number=i,
            title=f"Title {i}",
            narration=f"Narration for panel {i}",
            dialogue=f"Hero: Line {i}",
            image_prompt=f"SD prompt {i}"
        )
        for i in range(1, 6)
    ]
    story = StoryResponse(panels=panels)
    assert len(story.panels) == 5
