# Backend Setup Instructions

This document provides instructions for setting up the Python backend environment for the RPi-5-ASRS project.

## Prerequisites

- Python 3.11.x installed on your system
- Git (for cloning the repository)

## Installation

### 1. Create a virtual environment

From the `backend` directory:

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This will install all required Python packages including:
- FastAPI & Uvicorn (web framework)
- Piper-TTS (text-to-speech)
- Vosk (speech recognition)
- LangChain & Ollama (LLM integration)
- Sentence Transformers (embeddings)
- And all other dependencies

### 4. Download Piper voice models

Ensure you have the required Piper voice models in the `AIAssistant/voices/` directory:
- `en_US-bryce-medium.onnx` and `.onnx.json`
- `ar_JO-kareem-medium.onnx` and `.onnx.json`

## Running the Application

### Running individual services

**Alerts service** (port 8000):
```bash
.venv\Scripts\python.exe -m uvicorn app_alerts:app --host 0.0.0.0 --port 8000 --reload
```

**AI Assistant service** (port 8001):
```bash
.venv\Scripts\python.exe app_aiassistant.py
```

### Running from the frontend (recommended)

From the `frontend` directory:

```bash
npm run dev
```

This will automatically start both backend services along with the frontend.

## Project Structure

```
backend/
├── .venv/                  # Virtual environment (created during setup)
├── AIAssistant/           # AI Assistant module
│   ├── config.py          # Configuration
│   ├── inventory.py       # Inventory management
│   ├── llm.py             # LLM integration
│   ├── stt.py             # Speech-to-text
│   ├── tts.py             # Text-to-speech (Piper)
│   └── voices/            # Piper voice models
├── app_alerts.py          # Alerts FastAPI application
├── app_aiassistant.py     # AI Assistant FastAPI application
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### ModuleNotFoundError

If you encounter `ModuleNotFoundError`, ensure:
1. The virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. You're using the correct Python executable (from `.venv`)

### Port already in use

If ports 8000 or 8001 are already in use:
1. Stop any existing services using these ports
2. Or modify the port numbers in `package.json` (frontend directory)

### Virtual environment not found

If the virtual environment doesn't exist:
1. Create it: `python -m venv .venv`
2. Activate it
3. Install dependencies: `pip install -r requirements.txt`

## Development

### Updating dependencies

When adding new Python packages:

1. Install the package: `pip install package-name`
2. Update requirements.txt: `pip freeze > requirements.txt`
3. Commit both changes to version control

### Environment variables

Create a `.env` file in the backend directory for environment-specific configuration (e.g., API keys, database URLs).

## Notes

- The virtual environment (`.venv/`) is excluded from git via `.gitignore`
- Python 3.11.x is required for compatibility with all dependencies
- Large ML models (torch, transformers) may take time to download during installation
- Ensure sufficient disk space (~2-3GB) for all dependencies
