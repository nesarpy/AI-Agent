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
from modules.tools import *
from modules.Agent import Agent

# Load environment variables
dotenv.load_dotenv()
OPENROUTER_API = os.getenv("OPENROUTER_API_KEY")

def main():
    print("Configure AI")
    print("Use local gemma3:latest model via ollama - type True")
    print("Use openrouter api - type False")
    user_input = input()
    LOCAL = user_input.strip().lower() == "true"
    log(LOCAL)
    if LOCAL:
        print("Using local gemma3:latest model via ollama.")
        log("gemma3:latest via ollama")
    else:
        print("Using openrouter api")
        log("openrouter api")
    
    # Choose input method
    print("\nChoose input method:")
    print("1. Voice Control")
    print("2. Type Commands")
    input_choice = input("Enter 1 or 2: ").strip()
    
    INPUT_METHOD = "voice" if input_choice == "1" else "text"
    print(f"Using {INPUT_METHOD} input method")
    log(f"Input method: {INPUT_METHOD}")
    
    agent = Agent(local=LOCAL, openrouter_api=OPENROUTER_API, input_method=INPUT_METHOD)
    agent.run()

if __name__ == "__main__":
    main()

