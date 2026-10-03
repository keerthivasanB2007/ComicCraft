"""
ComicCraft - FastAPI Application Entry Point
"""
import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("comiccraft")

# Initialize directories
os.makedirs("static/panels", exist_ok=True)
os.makedirs("static/exports", exist_ok=True)
os.makedirs("static/css", exist_ok=True)

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Web-based AI comic creator using Gemini Flash, Gemini Pro, and Stable Diffusion",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include application routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Application health endpoint."""
    return {"status": "ok", "service": "ComicCraft-AI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
