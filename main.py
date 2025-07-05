"""
TODO:
- Add google tasks integration
"""

import requests
import dotenv
import os
import speech_recognition as sr
import json
import time
import webbrowser
import pyautogui
import subprocess

# Load environment variables
dotenv.load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
#add these to the env
macdemarco = os.getenv("MACD")
ye = os.getenv("YE")

# Simple configuration - edit these as needed
PLAY_BUTTON_COORDS = (431, 543)
SECOND_CLICK_COORDS = (426, 599)  # Second click position (for play button)

class VoiceControlAgent:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost",
            "Content-Type": "application/json"
        }
        
        # Command mappings
        self.command_handlers = {
            "Spotify": self.spotify,
            "Open": self.open_application,
            "Close": self.close_application,
            "Search": self.web_search,
            "Volume": self.volume_control,
            "Screenshot": self.take_screenshot,
            "TodoList": self.open_todo_list,
            "Website": self.open_website
        }
    
    def listen_for_voice(self) -> str:
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                print("Listening... Speak now!")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            print("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("No speech detected within timeout")
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
    
    def send_to_ai(self, voice_command: str) -> dict:
        """Send voice command to AI and get structured response"""
        try:
            # Read system prompt from file
            with open('systemprompt.txt', 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
        except FileNotFoundError:
            print("systemprompt.txt not found")

        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voice command: {voice_command}"}
            ]
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions", 
                headers=self.headers, 
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            ai_response = response.json()
            content = ai_response['choices'][0]['message']['content']
            
            # Parse JSON response
            try:
                # Clean up the response - remove markdown code blocks if present
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]  # Remove ```json
                if content.startswith('```'):
                    content = content[3:]   # Remove ```
                if content.endswith('```'):
                    content = content[:-3]  # Remove trailing ```
                
                content = content.strip()
                parsed_response = json.loads(content)
                return parsed_response
            except json.JSONDecodeError:
                print(f"Invalid JSON response from AI: {content}")
                return {"command": "Error", "parameters": "Invalid response format"}
                
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return {"command": "Error", "parameters": "API request failed"}
    
    def execute_command(self, command_data: dict):
        """Execute the parsed command"""
        command = command_data.get("command", "").lower()
        parameters = command_data.get("parameters", "")
        
        print(f"Executing: {command} with parameters: {parameters}")
        
        # Find and execute the appropriate handler
        for cmd_key, handler in self.command_handlers.items():
            if command.lower() == cmd_key.lower():
                handler(parameters)
                return
        
        print(f"Unknown command: {command}")
    
    def spotify(self, playlist: str):
        """Open Spotify and play the specified playlist/artist"""
        try:
            # Direct playlist URLs for specific artists
            artist_playlists = {
                "mac de marco": macdemarco,
                "kanye west": ye
            }
            
            # Check if it's a specific artist with direct playlist
            playlist_lower = playlist.lower()
            if playlist_lower in artist_playlists:
                search_url = artist_playlists[playlist_lower]
                print(f"Opening direct playlist for: {playlist}")
                
                # Open browser and navigate to URL
                webbrowser.open("https://www.google.com")
                time.sleep(2)
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(0.5)
                pyautogui.write(search_url)
                pyautogui.press('enter')
                
                # Wait for page to load and click play button
                time.sleep(7)
                pyautogui.click(PLAY_BUTTON_COORDS[0], PLAY_BUTTON_COORDS[1])
                print("Play button clicked!")
                
            else:
                # Use search for other artists/playlists
                search_url = f"https://open.spotify.com/search/{playlist.replace(' ', '%20')}"
                print(f"Searching Spotify for: {playlist}")
                
                # Open browser and navigate to URL
                webbrowser.open("https://www.google.com")  # Open browser first
                time.sleep(2)  # Wait for browser to open
                pyautogui.hotkey('ctrl', 'l')  # Select address bar
                time.sleep(0.5)
                pyautogui.write(search_url)
                pyautogui.press('enter')
                
                # Wait for page to load
                time.sleep(7)
                
                # For search results, click twice - first to select, then to play
                pyautogui.click(PLAY_BUTTON_COORDS[0], PLAY_BUTTON_COORDS[1])
                print("First click - selecting search result")
                time.sleep(2)  # Wait a bit between clicks
                pyautogui.click(SECOND_CLICK_COORDS[0], SECOND_CLICK_COORDS[1])
                print("Second click - playing music")
            
        except Exception as e:
            print(f"Error in Spotify function: {e}")
    
    def open_application(self, app_command: str):
        """Open specified application using Windows+R command"""
        try:
            # Open using Windows+R
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.write(app_command)
            pyautogui.press('enter')
            print(f"Opening: {app_command}")
        except Exception as e:
            print(f"Error opening {app_command}: {e}")
    
    def close_application(self, app_name: str):
        """Close specified application"""
        try:
            os.system(f"taskkill /f /im {app_name}.exe")
            print(f"Closing {app_name}")
        except Exception as e:
            print(f"Error closing {app_name}: {e}")
    
    def web_search(self, search_term: str):
        """Perform web search"""
        try:
            search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            
            # Open URL using Windows+R
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.write(search_url)
            pyautogui.press('enter')
            print(f"Searching for: {search_term}")
        except Exception as e:
            print(f"Error performing web search: {e}")
    
    def volume_control(self, action: str):
        """Control system volume"""
        try:
            if "up" in action.lower():
                pyautogui.press('volumeup')
                print("Volume increased")
            elif "down" in action.lower():
                pyautogui.press('volumedown')
                print("Volume decreased")
            elif "mute" in action.lower():
                pyautogui.press('volumemute')
                print("Volume muted")
        except Exception as e:
            print(f"Error controlling volume: {e}")
    
    def take_screenshot(self, filename: str = ""):
        """Take a screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            print(f"Screenshot saved as {filename}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")
    
    def open_todo_list(self, list_name: str):
        """Open Google Calendar tasks"""
        try:
            tasks_url = "https://calendar.google.com/calendar/u/0/r/tasks"
            
            # Open URL using Windows+R
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.write(tasks_url)
            pyautogui.press('enter')
            
            print(f"Opening Google Calendar tasks")
            
        except Exception as e:
            print(f"Error opening todo list: {e}")
    
    def open_website(self, website_url: str):
        """Open a specific website"""
        try:
            webbrowser.open(website_url)
            print(f"Opening website: {website_url}")
        except Exception as e:
            print(f"Error opening website: {e}")
    
    def run(self):
        """Main loop for the voice control agent"""
        print("AI Voice Control Agent Started!")
        print("Say 'exit' to quit")
        print("-" * 50)
        
        while True:
            # Listen for voice command
            voice_text = self.listen_for_voice()
            
            if not voice_text:
                continue
            
            # Check for exit command
            if "exit" in voice_text.lower() or "quit" in voice_text.lower():
                print("Goodbye!")
                break
            
            # Send to AI for processing
            command_data = self.send_to_ai(voice_text)
            
            # Execute the command
            self.execute_command(command_data)
            
            print("-" * 50)

def main():
    """Main function to run the voice control agent"""
    agent = VoiceControlAgent()
    agent.run()

if __name__ == "__main__":
    main()

