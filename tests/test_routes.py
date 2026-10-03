"""
Integration tests for FastAPI application routes.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import OutlineResponse, PanelOutline, StoryResponse, PanelStory

client = TestClient(app)


def test_get_root():
    """Test GET / renders the HTML form successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text
    assert "Story Prompt" in response.text
    assert "Generate 5-Panel Comic" in response.text


def test_get_export_success_page():
    """Test GET /export-success renders successfully."""
    response = client.get("/export-success")
    assert response.status_code == 200
    assert "PDF Export Status" in response.text


def test_get_test_image_endpoint():
    """Test GET /test-image endpoint."""
    response = client.get("/test-image")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "url" in data


@patch("app.routes.generate_outline")
@patch("app.routes.generate_story")
@patch("app.routes.generate_panel_images")
@patch("app.routes.build_comic_layout")
@patch("app.routes.save_pdf")
def test_post_generate_success(
    mock_pdf,
    mock_layout,
    mock_images,
    mock_story,
    mock_outline
):
    """Test POST /generate runs full pipeline and renders preview."""
    # Setup mocks
    mock_outline.return_value = OutlineResponse(
        panels=[
            PanelOutline(panel_number=i, title=f"T{i}", scene_description=f"D{i}", image_prompt=f"P{i}")
            for i in range(1, 6)
        ]
    )

    mock_story.return_value = StoryResponse(
        panels=[
            PanelStory(
                panel_number=i,
                title=f"Scene {i}",
                narration=f"Narration {i}",
                dialogue=f"Character: Dialogue {i}",
                image_prompt=f"Prompt {i}"
            )
            for i in range(1, 6)
        ]
    )

    mock_images.return_value = [f"static/panels/panel_{i}.png" for i in range(1, 6)]
    mock_layout.return_value = "static/exports/final_comic.png"
    mock_pdf.return_value = "static/exports/comic_story.pdf"

    payload = {
        "story_prompt": "A courageous astronaut discovers an ancient alien portal.",
        "character_name": "Aria",
        "setting": "Lunar Crater",
        "tone": "Adventure",
        "art_style": "Anime"
    }

    response = client.post("/generate", data=payload)
    assert response.status_code == 200
    assert "Your 5-Panel Comic Story" in response.text
    assert "Aria" in response.text
    assert "Lunar Crater" in response.text
    assert "Download PDF" in response.text


def test_post_generate_invalid_input():
    """Test POST /generate with missing/empty fields returns 400."""
    payload = {
        "story_prompt": "   ",
        "character_name": "Aria",
        "setting": "Lunar Crater",
        "tone": "Adventure",
        "art_style": "Anime"
    }
    response = client.post("/generate", data=payload)
    assert response.status_code == 400
    assert "Invalid form input" in response.text
