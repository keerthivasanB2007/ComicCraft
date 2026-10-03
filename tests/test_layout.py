"""
Unit tests for layout builder service.
"""
import os
import pytest
from PIL import Image
from app.services.layout_builder import build_comic_layout, wrap_text, load_font
from app.models.schemas import PanelStory


@pytest.fixture
def mock_panel_images(tmp_path):
    """Create 5 test images for layout testing."""
    image_paths = []
    for i in range(1, 6):
        img_path = str(tmp_path / f"mock_panel_{i}.png")
        img = Image.new("RGB", (512, 512), color=(i * 40, 100, 200))
        img.save(img_path)
        image_paths.append(img_path)
    return image_paths


def test_build_comic_layout(mock_panel_images, tmp_path):
    """Test 5-panel layout composition generates expected comic image."""
    panels = [
        PanelStory(
            panel_number=i,
            title=f"Scene {i}",
            narration=f"A crucial event occurs in chapter {i}.",
            dialogue=f"Hero: Let's move forward panel {i}!",
            image_prompt=f"Prompt {i}"
        )
        for i in range(1, 6)
    ]

    output_comic_path = str(tmp_path / "test_final_comic.png")
    result_path = build_comic_layout(
        panels=panels,
        image_paths=mock_panel_images,
        output_path=output_comic_path
    )

    assert os.path.exists(result_path)
    with Image.open(result_path) as img:
        assert img.width > 1000
        assert img.height > 1000


def test_wrap_text_function():
    """Test text wrapping utility."""
    font = load_font(20)
    dummy_img = Image.new("RGB", (100, 100))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(dummy_img)

    long_text = "This is a very long sentence designed to test whether word wrapping breaks text into multiple lines."
    lines = wrap_text(draw, long_text, font, max_width=150)
    assert len(lines) > 1
