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
from logger import log
from modules.utils import *
from modules.Agent import Agent

# Load environment variables
dotenv.load_dotenv()
OPENROUTER_API = os.getenv("OPENROUTER_API_KEY")

def main():
    print("Configure AI")
    print("Use local gemma3:latest model via ollama - type True")
    print("Use deepseek via openrouter api - type False")
    user_input = input()
    LOCAL = user_input.strip().lower() == "true"
    log(LOCAL)
    if LOCAL:
        print("Using local gemma3:latest model via ollama.")
        log("gemma3:latest via ollama")
    else:
        print("Using deepseek via openrouter api")
        log("Deepseek via openrouter api")
    agent = Agent(local=LOCAL, openrouter_api=OPENROUTER_API)
    agent.run()

if __name__ == "__main__":
    main()

