"""
Pydantic Schemas for ComicCraft
"""
from typing import List
from pydantic import BaseModel, Field, field_validator


class ComicRequest(BaseModel):
    """Input payload for generating a comic."""
    story_prompt: str = Field(..., min_length=3, description="Core storyline prompt")
    character_name: str = Field(..., min_length=1, description="Main character name")
    setting: str = Field(..., min_length=1, description="Story environment or setting")
    tone: str = Field(..., min_length=1, description="Tone of the story (e.g., Funny, Dramatic)")
    art_style: str = Field(..., min_length=1, description="Art style (e.g., Manga, Anime, American, Belgian)")

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def check_not_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be blank or contain only whitespace.")
        return stripped


class PanelOutline(BaseModel):
    """Structured outline for a single comic panel from Gemini Flash."""
    panel_number: int = Field(..., ge=1, le=5, description="Panel index from 1 to 5")
    title: str = Field(..., min_length=1, description="Short title for the panel")
    scene_description: str = Field(..., min_length=1, description="Background and character visual description")
    image_prompt: str = Field(..., min_length=1, description="Visual prompt for image generator")


class OutlineResponse(BaseModel):
    """Full 5-panel structured outline."""
    panels: List[PanelOutline] = Field(..., description="List of exactly 5 panel outlines")

    @field_validator("panels")
    @classmethod
    def validate_five_panels(cls, panels: List[PanelOutline]) -> List[PanelOutline]:
        if len(panels) != 5:
            raise ValueError(f"Outline must contain exactly 5 panels, got {len(panels)}")
        # Check panel numbering
        panel_nums = [p.panel_number for p in panels]
        if sorted(panel_nums) != [1, 2, 3, 4, 5]:
            raise ValueError(f"Panels must be numbered 1 to 5, got {panel_nums}")
        return panels


class PanelStory(BaseModel):
    """Detailed story, narration, and dialogue for a panel from Gemini Pro."""
    panel_number: int = Field(..., ge=1, le=5, description="Panel index from 1 to 5")
    title: str = Field(..., min_length=1, description="Panel title")
    narration: str = Field(..., description="Narrative text or caption")
    dialogue: str = Field(..., description="Character dialogue or spoken line")
    image_prompt: str = Field(..., min_length=1, description="Refined visual prompt for image generation")


class StoryResponse(BaseModel):
    """Full 5-panel detailed story response."""
    panels: List[PanelStory] = Field(..., description="List of exactly 5 detailed panel stories")

    @field_validator("panels")
    @classmethod
    def validate_five_panels(cls, panels: List[PanelStory]) -> List[PanelStory]:
        if len(panels) != 5:
            raise ValueError(f"Story must contain exactly 5 panels, got {len(panels)}")
        panel_nums = [p.panel_number for p in panels]
        if sorted(panel_nums) != [1, 2, 3, 4, 5]:
            raise ValueError(f"Panels must be numbered 1 to 5, got {panel_nums}")
        return panels


class ComicResult(BaseModel):
    """Final output object containing paths and panel details."""
    request: ComicRequest
    panels: List[PanelStory]
    panel_image_urls: List[str]
    comic_image_url: str
    pdf_url: str
