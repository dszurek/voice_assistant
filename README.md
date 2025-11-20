# EcoCAR Voice Assistant

> A simple, modular voice assistant prototype built for The University of Alabama's EcoCAR EV Challenge competition vehicle; supports wake-word detection, speech-to-text (STT), chat-based responses, and text-to-speech (TTS).

---

## 🚀 Overview

This repository is a prototype voice assistant designed for the EcoCAR platform. It is built using a set of small independent services that together provide a usable in-vehicle voice interaction experience:

- Wake word detection via openwakeword
- Speech-to-text using OpenAI Whisper
- Chat responses via an LLM (Ollama through LangChain)
- Interaction and infotainment control logic
- Text-to-speech synthesis using Suno/BARK and pyttsx3

The codebase is organized in a set of service-level modules to keep concerns separated and make it easy to extend, test, or integrate with the car's infotainment stack.

---

## 🧭 Features

- Hot-word / wake-word detection (e.g. "Hey Jarvis")
- Live audio capture from the microphone, STT transcription, and TTS response playback
- Modular chat service that uses LangChain + Ollama to generate short, concise responses
- Interaction service for simple vehicle commands (e.g., play music, set navigation, toggle headlights)
- Dockerfile and pyinstaller build targets for packaging

---

## 📁 Project Structure

At the top-level, you'll find the service modules and the application entrypoint: a `voice_assistant/` folder with:

- `app.py` — small example runner that starts Wake Word service
- `wakeword_service/` — wake word detection (openwakeword)
- `speech_service/` — STT (`stt.py`) and TTS (`tts.py`) implementations
- `chat_service/` — chat integration (LangChain + Ollama wrapper)
- `interaction_service/` — simple vehicle-perception and command handling
- `Dockerfile` — container build
- `pyproject.toml` / `requirements.txt` — dependencies
- `tests/` — testing (empty placeholder)

---

## 🧩 Requirements

- Python 3.10 <= 3.12
- A microphone and speaker for interactive usage
- Optional: GPU for model acceleration (Whisper / Bark), recommended if using larger models
- For Windows audio capture: ensure `PyAudio` works; consider running in WSL or native if you encounter driver issues

---

## ⚡ Quickstart (Local)

You can run the project either using a virtual environment (recommended) or using `poetry` (if you prefer). Examples below use PowerShell on Windows; adapt for Bash on macOS/Linux.

### Clone the repo

```pwsh
git clone <repo-url> ecocar-voice-assistant
cd ecocar-voice-assistant/voice_assistant
```

### Option 1 — pip + venv (Windows PowerShell)

```pwsh
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Option 2 — Poetry

```pwsh
poetry install
poetry run python app.py
```

What to expect: when you run `app.py` the program will ask you to press Enter to begin listening. The wake-word listener will start; when it detects the wake word it will:

1. Play a short sound to indicate detection
2. Record a short segment of audio
3. Transcribe the audio with Whisper
4. Use the Interaction Service to determine whether the text is a vehicle command
5. If not a command, send the text to the Chat Service (Ollama via LangChain)
6. Convert the response to speech using the TTS service

---

## 🛠️ Docker

The included `Dockerfile` builds a single-file executable using `pyinstaller` and installs required audio and build-related packages.

> Important: Running microphone/speaker in containers varies depending on host OS. On Linux you can pass device access; on Windows, audio passthrough to a container may not be native. If targeting a Windows host, consider running the app locally or using WSL.

### Build image

```pwsh
docker build -t ecocar-voice-assistant:latest .
```

### Run (Linux example with audio passthrough)

```bash
# Add sound device access for Linux host
docker run --rm -it --device /dev/snd -v /dev/snd:/dev/snd --name ecocar-voice ecocar-voice-assistant:latest
```

If you don't have audio devices available to the container, you can still run the app but it won't be able to record or play audio.

---

## 🧪 Testing

There are no automated tests added yet (placeholder in `tests/`). Recommended approach:

- Add unit tests for each service (e.g., InteractionService is a good candidate for pure unit tests)
- Use `pytest` for running tests

To install test dependencies and run tests:

```pwsh
pip install pytest
pytest -q
```

---

## 🔧 Development Notes / Contributing

If you want to extend the project or contribute:

- Keep each feature as a modular service for easier testing
- When adding new dependencies, update `pyproject.toml` (or `requirements.txt`) and include instructions in README
- Linting and pre-commit hooks are recommended (this repo includes `pre-commit` in `pyproject.toml`)
- Add tests to the `tests/` folder and include test instructions in the README

Suggested PR checklist:

- Run unit tests
- Add or update a changelog entry
- Add documentation for any public API or interface changes

---

## 💡 Tips & Troubleshooting

- PyAudio installation can be problematic on Windows; if you're on Windows, install the appropriate wheel for your Python version or use WSL where `apt` can install `libportaudio2` and related dependencies.
- If using Ollama or any local model backend, ensure the backend is running and reachable; all network and LLM configs are environment-dependent and may need additional setup.
- If you see errors about missing models: `openwakeword` will attempt to download models at runtime; ensure your container or machine has internet to fetch them.

---
