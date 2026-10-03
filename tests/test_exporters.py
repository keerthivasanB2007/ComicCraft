"""
Unit tests for PDF export service.
"""
import os
import pytest
from PIL import Image
from app.services.exporters import save_pdf


def test_save_pdf(tmp_path):
    """Test generating a valid PDF from a composite comic image."""
    mock_comic = str(tmp_path / "mock_comic.png")
    img = Image.new("RGB", (1200, 1600), color=(30, 40, 60))
    img.save(mock_comic)

    output_pdf = str(tmp_path / "output_story.pdf")
    saved_path = save_pdf(comic_image_path=mock_comic, pdf_path=output_pdf)

    assert os.path.exists(saved_path)
    assert os.path.getsize(saved_path) > 1000  # Non-empty PDF


def test_save_pdf_missing_file():
    """Test save_pdf raises FileNotFoundError on non-existent input."""
    with pytest.raises(FileNotFoundError):
        save_pdf("non_existent_image_path_123.png", "output.pdf")
