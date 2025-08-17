import requests
import speech_recognition as sr
import json
import time
import os
from logger import log
from modules.utils import *

class Agent:
    def __init__(self, local=False, openrouter_api=None):
        self.local = local
        self.openrouter_api = openrouter_api
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        if self.local:
            self.headers = {
                "Content-Type": "application/json"
            }
        else:
            self.headers = {
                "Authorization": f"Bearer {self.openrouter_api}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://slimeydev.github.io/",
                "X-Title": "AI Computer Agent"
            }
        
        # Command mappings - these will call utility functions from utils module
        self.command_handlers = {
            "Spotify": self.spotify,
            "Open": open_application,
            "Close": close_application,
            "Search": web_search,
            "Volume": volume_control,
            "Screenshot": take_screenshot,
            "TodoList": open_todo_list,
            "Website": open_website,
            "Shutdown": shutdown_system,
            "Restart": restart_system,
            "Sleep": sleep_system,
            "Hibernate": hibernate_system,
            "File": open_file
        }
    
    def listen_for_voice(self) -> str:
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source)
                
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            log(f"You said: {text}")
            return text
            
        except sr.UnknownValueError:
            print("Could not understand audio")
            log("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            log(f"Could not request results; {e}")
            return ""
    
    def send_to_ai(self, voice_command: str) -> dict:
        """Send voice command to local Ollama and get structured response"""
        try:
            # Read system prompt from file
            with open('systemprompt.txt', 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
        except FileNotFoundError:
            print("systemprompt.txt not found")
            log("systemprompt.txt not found")

        if self.local:
            model = "gemma3:latest"
        else:
            model = "tngtech/deepseek-r1t2-chimera:free"
        
        data = {
            "model": model,
            "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Voice command: {voice_command}"}
            ]
        }

        try:

            if self.local:
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    headers={"Content-Type": "application/json"},
                    json=data,
                    stream=False
                )
                response.raise_for_status()
                ai_response = response.json()
                content = ai_response['message']['content']
            else:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions", 
                    headers=self.headers, 
                    json=data,
                    timeout=30
                )

                response.raise_for_status()
                ai_response = response.json()
                content = ai_response['choices'][0]['message']['content']


            # Parse JSON response
            try:
                content = extract_json(content)
                parsed_response = json.loads(content)
                return parsed_response
            except json.JSONDecodeError:
                log(f"Invalid JSON response from AI: {content}")
                return {"command": "Error", "parameters": "Invalid response format"}

        except requests.RequestException as e:
            log(f"API request failed: {e}")
            return {"command": "Error", "parameters": "API request failed"}
    
    def execute_command(self, command_data: dict):
        """Execute the parsed command"""
        command = command_data.get("command", "").lower()
        parameters = command_data.get("parameters", "")
        
        log(f"Executing: {command} with parameters: {parameters}")
        
        # Find and execute the appropriate handler
        for cmd_key, handler in self.command_handlers.items():
            if command.lower() == cmd_key.lower():
                handler(parameters)
                return
        
        print(f"Unknown command: {command}")
        log(f"Unknown command: {command}")
    
    def spotify(self, playlist: str):
        """Open Spotify and search for the specified artist/playlist"""
        try:
            # Always use search for any artist/playlist
            search_url = f"https://open.spotify.com/search/{playlist.replace(' ', '%20')}"
            print(f"Searching Spotify for: {playlist}")
            log(f"Searching Spotify for: {playlist}")
            
            # Open browser and navigate to URL
            spotifyWeb(search_url)
            
            # Wait for page to load
            time.sleep(7)
            
            # For search results, click twice - first to select, then to play
            click(PLAY_BUTTON_COORDS)
            log("First click - selecting search result")
            time.sleep(2)  # Wait a bit between clicks
            location = locateButton()
            if location != None:
                click(location)
            else:
                click(SECOND_CLICK_COORDS)
            log("Second click - playing music")
            
        except Exception as e:
            log(f"Error in Spotify function: {e}")
            print("Error, check logs for more info")
    
    def run(self):
        """Main loop for the voice control agent"""
        print("AI Voice Control Agent Started!")
        log("="*50)
        log("Agent started")
        print("Say 'exit' to quit")
        print("-"*50)
        
        while True:
            # Listen for voice command
            voice_text = self.listen_for_voice()
            
            if not voice_text:
                continue
            
            # Check for exit command
            if "exit" in voice_text.lower() or "quit" in voice_text.lower():
                print("Goodbye!")
                log("Exited")
                log("="*50)
                break
            
            # Send to AI for processing
            command_data = self.send_to_ai(voice_text)
            
            # Execute the command
            self.execute_command(command_data)
            
            print("-" * 50) 