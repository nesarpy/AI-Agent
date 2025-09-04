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

- Configure the program via `config.json` at the project root.

### Fields

- **use_local_model**: `true` to use your local Ollama model; `false` to use OpenRouter.
- **local_model_name**: Model name served by Ollama (e.g., `gemma3:latest`).
- **cloud_model_name**: OpenRouter model identifier (e.g., `mistralai/mixtral-8x7b-instruct`).
- **input_method**: `voice` or `text`.
- **openrouter_api_key_env**: Name of the environment variable holding your OpenRouter API key (default `OPENROUTER_API_KEY`).

### Notes

- On startup, the app reads `config.json`. If missing, it uses safe defaults.
- `modules/tools.py` uses `TESSERACT_PATH` when available; otherwise it falls back to a standard install path.
- Save the environmental variables to a `.env` file with the respective names.
