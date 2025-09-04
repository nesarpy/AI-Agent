import requests
import dotenv
import os
import speech_recognition as sr
import json
import time
import webbrowser
import pyautogui
import subprocess
import glob
from pathlib import Path
import re
from logger import logger
from modules.tools import *
from modules.Agent import Agent

# Load environment variables
dotenv.load_dotenv()
OPENROUTER_API = os.getenv("OPENROUTER_API_KEY")

def main():
    # Load config
    config = {}
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("config.json not found, using defaults")
        logger.warning("config.json not found, using defaults")
    except Exception as e:
        logger.error(f"Error reading config.json: {e}")

    # Resolve settings with defaults
    use_local = bool(config.get("use_local_model", True))
    input_method = config.get("input_method", "text")
    local_model_name = config.get("local_model_name", "gemma3:latest")
    cloud_model_name = config.get("cloud_model_name", "mistralai/mixtral-8x7b-instruct")
    http_referer = config.get("http_referer", "https://nesarpy.github.io/")

    # Announce mode
    if use_local:
        print(f"Using local model: {local_model_name}")
        logger.info(f"Using local model: {local_model_name}")
    else:
        print("Using OpenRouter API")
        logger.info("Using OpenRouter API")

    print(f"Using {input_method} input method")
    logger.info(f"Input method: {input_method}")

    agent = Agent(
        local=use_local,
        openrouter_api=OPENROUTER_API,
        input_method=input_method,
        local_model_name=local_model_name,
        cloud_model_name=cloud_model_name,
        http_referer=http_referer
    )
    agent.run()

if __name__ == "__main__":
    main()

