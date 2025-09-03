# AI Agent

A voice-controlled AI assistant that uses natural language to control your computer.

## Features

* Voice recognition with microphone input
* AI processing via OpenRouter with JSON responses
* Control applications, websites, and system functions
* Spotify integration for music
* Web search and navigation

## Example Commands

* "Play some jazz on Spotify"
* "Open YouTube"
* "Open Notepad"
* "Turn volume up"
* "Search for Python tutorials"

## Configuration

### Setup

- Copy `config.json.example` to `config.json` at the project root.
- Adjust values as needed. Do not commit `config.json` (keep only the example in Git).

### Fields

- **use_local_model**: `true` to use your local Ollama model; `false` to use OpenRouter.
- **local_model_name**: Model name served by Ollama (e.g., `gemma3:latest`).
- **cloud_model_name**: OpenRouter model identifier (e.g., `mistralai/mixtral-8x7b-instruct`).
- **input_method**: `voice` or `text`.
- **openrouter_api_key_env**: Name of the environment variable holding your OpenRouter API key (default `OPENROUTER_API_KEY`).
- **http_referer** and **x_title**: Metadata headers sent to OpenRouter.
- **tesseract_path_env**: Env var name for Tesseract path (default `TESSERACT_PATH`).
- **tesseract_path_default**: Fallback path used if the env var is not set.

### Notes

- On startup, the app reads `config.json`. If missing, it uses safe defaults.
- `modules/tools.py` uses `TESSERACT_PATH` when available; otherwise it falls back to a standard install path.
- Save the environmental variables to a `.env` file with the respective names.
