# ComicCraft - AI Comic Story Creator using Gemini Models

> **A Web-based AI Comic Story Creator powered by Google Gemini (Flash & Pro), Stable Diffusion, FastAPI, and ReportLab.**

---

## 📖 Project Overview

**ComicCraft** is an end-to-end automated artificial intelligence application that transforms text scenarios and character concepts into structured, illustrated, and fully formatted **5-panel comic strips**.

The project uses a two-stage Large Language Model (LLM) pipeline combined with diffusion-based image generation to create cohesive visual storytelling:
1. **Gemini Flash** generates a structured, pacing-conscious 5-panel comic storyboard outline.
2. **Gemini Pro** expands the outline into rich story narration, punchy character dialogue, and refined text-to-image prompts.
3. **Stable Diffusion (Hugging Face Diffusers)** renders high-detail illustrations for each individual panel.
4. **Pillow Layout Engine** adds styled caption boxes, outlines dialogue, and composites all 5 panels into a publication-ready comic strip.
5. **ReportLab Exporter** compiles the comic into an A4 printable PDF document.

---

## ⚡ Key Features

- **Two-Stage Gemini LLM Pipeline:**
  - `gemini-1.5-flash`: Fast, structured JSON storyboard outlining.
  - `gemini-1.5-pro`: Deep narrative and dialogue scriptwriting.
- **5-Panel Comic Layout:** Features a 2-2-1 layout structure (two top panels, two middle panels, and a prominent climax panel) with clear narrative progression.
- **Customizable Story Parameters:**
  - Story Prompt
  - Main Character Name
  - Setting / Environment
  - Tone (*Funny, Adventure, Dramatic, Inspirational, Mystery*)
  - Art Style (*Manga, Anime, American, Belgian*)
- **High-Fidelity Text-to-Image Generation:** Powered by Stable Diffusion via Hugging Face Diffusers.
- **Dialogue & Caption Overlay:** Automatic multiline text wrapping, high-contrast text outlines, and structured caption borders.
- **Interactive Web Interface:** Modern, responsive HTML5/CSS3 frontend rendered via FastAPI and Jinja2 templates.
- **Direct PDF Export:** Generates downloadable A4 PDF documents ready for printing.
- **Comprehensive Automated Test Suite:** Unit and integration tests with mocked AI APIs for offline CI/CD verification.

---

## 🏗️ Architecture & Pipeline Flow

```text
       ┌────────────────────────────────────────────────────────┐
       │                   User Web Browser                     │
       │  (Prompt, Character Name, Setting, Tone, Art Style)    │
       └───────────────────────────┬────────────────────────────┘
                                   │ HTTP POST /generate
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                   FastAPI Backend                      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ 1. Gemini Flash Service (`app/services/gemini_flash.py`)│
       │    • Generates 5-Panel Structured JSON Outline         │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ 2. Gemini Pro Service (`app/services/gemini_pro.py`)   │
       │    • Refines Narration, Dialogue & Visual Prompts      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ 3. Image Generator (`app/services/image_generator.py`) │
       │    • Stable Diffusion / Diffusers Panel Rendering      │
       │    • Saves `static/panels/panel_1.png` ... `panel_5.png`│
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ 4. Layout Builder (`app/services/layout_builder.py`)   │
       │    • Pillow Dialogue Wrapping, Borders & 5-Panel Grid  │
       │    • Saves `static/exports/final_comic.png`            │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ 5. PDF Exporter (`app/services/exporters.py`)          │
       │    • ReportLab A4 Document Assembly                    │
       │    • Saves `static/exports/comic_story.pdf`            │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │ Jinja2 Comic Preview & PDF Download (`comic_preview.html`)│
       └────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Component / Library | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+, FastAPI, Uvicorn | RESTful server and application routing |
| **Frontend** | HTML5, CSS3, Jinja2 | Modern responsive web UI and templates |
| **Validation** | Pydantic v2 | Strict schema validation for requests and LLM outputs |
| **LLM Stage 1** | Google Gemini Flash (`gemini-1.5-flash`) | 5-panel structured outline generation |
| **LLM Stage 2** | Google Gemini Pro (`gemini-1.5-pro`) | Story narrative, character dialogue & prompt expansion |
| **Image Generation** | Stable Diffusion (`diffusers`, `torch`) | High-resolution comic panel illustration |
| **Image Processing** | Pillow (PIL) | Text wrapping, stroked captions, and 5-panel layout compositing |
| **PDF Generation** | ReportLab | Formatted A4 PDF generation with aspect preservation |
| **Testing** | Pytest, FastAPI TestClient | Offline automated unit and integration tests |

---

## 📁 Project Structure

```text
ComicCrafter-AI/
├── app/
│   ├── __init__.py               # App package initialization
│   ├── main.py                   # FastAPI initialization & static mounting
│   ├── routes.py                 # Endpoint routes (GET /, POST /generate, etc.)
│   ├── models/
│   │   ├── __init__.py           # Models exports
│   │   └── schemas.py            # Pydantic validation schemas
│   └── services/
│       ├── __init__.py           # Service exports
│       ├── gemini_flash.py       # Gemini Flash 5-panel outline service
│       ├── gemini_pro.py         # Gemini Pro story expansion service
│       ├── image_generator.py    # Stable Diffusion / Diffusers synthesizer
│       ├── layout_builder.py     # Pillow 5-panel comic compositing engine
│       └── exporters.py          # ReportLab PDF exporter
│
├── templates/
│   ├── index.html                # Main story generation form
│   ├── comic_preview.html        # Comic preview with individual panels and full strip
│   └── export_success.html       # PDF export and download status page
│
├── static/
│   ├── css/
│   │   └── style.css             # Modern comic-themed stylesheet
│   ├── panels/                   # Directory for generated individual panel images
│   └── exports/                  # Directory for composite comic and PDF exports
│
├── tests/
│   ├── __init__.py               # Test package initialization
│   ├── test_schemas.py           # Data validation tests
│   ├── test_gemini.py            # Mocked Flash & Pro pipeline tests
│   ├── test_layout.py            # Layout builder and text-wrapping tests
│   ├── test_exporters.py         # ReportLab PDF creation tests
│   └── test_routes.py            # FastAPI route integration tests
│
├── .env.example                  # Environment configuration template
├── .gitignore                    # Version control ignore rules
├── requirements.txt              # Production and test dependencies
└── README.md                     # Comprehensive project documentation
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Kashish415/ComicCrafter-AI.git
cd ComicCrafter-AI
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your Google Gemini API Key:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_FLASH_MODEL=gemini-1.5-flash
GEMINI_PRO_MODEL=gemini-1.5-pro
SD_MODEL_ID=runwayml/stable-diffusion-v1-5
```

---

## 💻 Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
```text
http://127.0.0.1:8000
```

---

## 🧪 Running Automated Tests

Run the complete test suite with pytest:

```bash
pytest -v
```

All external Gemini and Stable Diffusion calls are mocked during tests, allowing instant, offline verification.

---

## ⚠️ Limitations & Resource Considerations

- **Stable Diffusion Hardware Requirements:** Running local Stable Diffusion requires a CUDA-capable GPU with $\ge 6\text{ GB}$ VRAM. When running on low-resource environments (or CPU-only machines), `image_generator.py` utilizes a fallback visual synthesizer to ensure the application executes end-to-end without crashing.
- **Gemini API Limits:** Free-tier Gemini API keys have rate limits per minute.

---

## 🔮 Future Scope

- Support for multi-page comic book chapters.
- Fine-tuned comic character LoRA models for cross-panel character consistency.
- Speech bubble vector placement directly over characters using object detection.
- Multi-language localization for dialogue generation.

---

## 📄 License & Attribution

Developed for the Software Development Capstone (SDC) Project.  
Powered by Google Gemini Models and Hugging Face Diffusers.
