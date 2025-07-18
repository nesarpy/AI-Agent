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

# Load environment variables
dotenv.load_dotenv()
OPENROUTER_API = os.getenv("OPENROUTER_API_KEY")

PLAYLISTS = {
    "mac de marco": os.getenv("MACD"),
    "kanye west": os.getenv("YE"),
    "the smiths": os.getenv("SMITHS"),
    "playlist_1": os.getenv("PLAYLIST1"),
    "playlist_2": os.getenv("PLAYLIST2"),
    "jayz": os.getenv("JAYZ"),
    "laufey": os.getenv("LAUFEY"),
    "tyler the creator": os.getenv("TYLER")
}

PLAY_BUTTON_COORDS = (431, 543)
SECOND_CLICK_COORDS = (426, 599)

def click(location):
    """Moves mouse button to location then clicks in a more human like way"""
    pyautogui.moveTo(*location)
    time.sleep(0.1)
    log("Mouse down")
    pyautogui.mouseDown(*location)
    time.sleep(0.1)
    log("Mouse up")
    pyautogui.mouseUp(*location)

def spotifyWeb(url):
    """Opens spotify web"""
    webbrowser.open("https://google.com")
    time.sleep(2)
    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.1)
    pyautogui.write(url)
    pyautogui.press("enter")

def locateButton():
    """Locates playbutton on screen"""
    # add more reference images if you want
    reference_images = [
        "imgrec/ref1.png",
        "imgrec/ref2.png",
        "imgrec/ref3.png"
    ]

    location = None

    for image in reference_images:
        location = pyautogui.locateOnScreen(image, confidence=0.85)
        if location:
            x,y = pyautogui.center(location)
            log(f"Found playbutton using {image}")
            return x, y
    
    # if no image is matched, return None
    return location

def extract_json(text):
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r'```(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

class VoiceControlAgent:
    def __init__(self, local=False):
        self.local = local
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        if self.local:
            self.headers = {
                "Content-Type": "application/json"
            }
        else:
            self.headers = {
                "Authorization": f"Bearer {OPENROUTER_API}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://slimeydev.github.io/",
                "X-Title": "AI Computer Agent"
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
            "Website": self.open_website,
            "Shutdown": self.shutdown_system,
            "Restart": self.restart_system,
            "Sleep": self.sleep_system,
            "Hibernate": self.hibernate_system,
            "File": self.open_file
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
            model = "tngtech/deepseek-r1t2-chimera:free",
        
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
                    timeout=120,
                    stream=True
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
        """Open Spotify and play the specified playlist/artist"""
        try:
            # Check if it's a specific artist with direct playlist
            if playlist.lower() in PLAYLISTS:
                search_url = PLAYLISTS[playlist.lower()]
                print(f"Opening direct playlist for: {playlist}")
                log(f"Opening direct playlist for: {playlist}")
                
                # Open browser and navigate to URL
                spotifyWeb(search_url)
                
                # Wait for page to load and click play button
                time.sleep(10)
                log("Finding playbutton")
                location = locateButton()
                if location != None:
                    click(location)
                else:
                    click(PLAY_BUTTON_COORDS)
                log("Play button clicked!")
            else:
                # Use search for other artists/playlists
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
    
    def open_application(self, app_command: str):
        """Open specified application using Windows+R command"""
        try:
            # Open using Windows+R
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.write(app_command)
            pyautogui.press('enter')
            print(f"Opening: {app_command}")
            log(f"Opening: {app_command}")
        except Exception as e:
            log(f"Error opening {app_command}: {e}")
            print("Error, check logs")
    
    def close_application(self, app_name: str):
        """Close specified application"""
        try:
            os.system(f"taskkill /f /im {app_name}.exe")
            print(f"Closing {app_name}")
            log(f"Closing {app_name}")
        except Exception as e:
            log(f"Error closing {app_name}: {e}")
            print("Error, check logs")
    
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
            log(f"Error performing web search: {e}")
            print("Error, check logs")
    
    def volume_control(self, action: str):
        """Control system volume"""
        try:
            action_lower = action.lower()
            
            if "up" in action_lower:
                for i in range(10):
                    pyautogui.press('volumeup')
                print("Volume increased")
            elif "down" in action_lower:
                for i in range(10):
                    pyautogui.press('volumedown')
                print("Volume decreased")
            elif "mute" in action_lower:
                pyautogui.press('volumemute')
                print("Volume muted")
            elif "volume" in action_lower:
                # Extract number from action (e.g., "volume 50" -> 50)
                numbers = re.findall(r'\d+', action)
                if numbers:
                    target_volume = int(numbers[0])
                    if 0 <= target_volume <= 100:
                        # Set volume to specific level
                        self.set_volume_to_level(target_volume)
                        print(f"Volume set to {target_volume}%")
                    else:
                        print("Volume must be between 0 and 100")
                else:
                    print("Please specify a volume level (0-100)")
            else:
                print("Volume command not recognized. Use: up, down, mute, or volume [0-100]")
                
        except Exception as e:
            log(f"Error controlling volume: {e}")
            print("Error, check logs")
    
    def set_volume_to_level(self, target_level: int):
        """Set volume to a specific percentage level"""
        try:
            for i in range(50):  # start volume at 0
                pyautogui.press('volumedown')
            
            presses_needed = int(target_level / 2)
            for i in range(presses_needed):
                pyautogui.press('volumeup')
                
        except Exception as e:
            log(f"Error setting volume level: {e}")
            print("Error, check logs")
    
    def take_screenshot(self, filename: str = ""):
        """Take a screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            print(f"Screenshot saved as {filename}")
            log(f"Screenshot saved as {filename}")
        except Exception as e:
            log(f"Error taking screenshot: {e}")
            print("Error, check logs")
    
    def open_todo_list(self, list_name: str):
        """Open Google Calendar tasks"""
        try:
            tasks_url = "https://calendar.google.com/calendar/u/0/r/tasks"
            
            # Open URL using Windows+R
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.write(tasks_url)
            pyautogui.press('enter')
            
            log(f"Opening Google Calendar tasks")
            
        except Exception as e:
            log(f"Error opening todo list: {e}")
            print("Error, check logs")
    
    def open_website(self, website_url: str):
        """Open a specific website"""
        try:
            webbrowser.open(website_url)
            log(f"Opening website: {website_url}")
        except Exception as e:
            log(f"Error opening website: {e}")
            print("Error, check logs")
    
    def shutdown_system(self, action: str):
        """Shutdown the system"""
        try:
            if "now" in action.lower():
                os.system("shutdown /s /t 0")
                print("System shutting down")
                log("Shutting down system")
            else:
                print("Shutdown command not recognized")
                log("Shutdown command not recognized")
        except Exception as e:
            log(f"Error shutting down system: {e}")
            print("Error, check logs")
    
    def restart_system(self, action: str):
        """Restart the system"""
        try:
            if "now" in action.lower():
                os.system("shutdown /r /t 0")
                print("System restarting")
                log("restarting system")
            else:
                print("Restart command not recognized")
                log("restart command not recognized")
        except Exception as e:
            log(f"Error restarting system: {e}")
            print("Error, check logs")
    
    def sleep_system(self, action: str):
        """Put the system to sleep"""
        try:
            if "now" in action.lower():
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                print("System going to sleep")
                log("System going to sleep")
            else:
                print("Sleep command not recognized")
                log("sleep command not recognized")
        except Exception as e:
            log(f"Error putting system to sleep: {e}")
            print("Error, check logs")
    
    def hibernate_system(self, action: str):
        """Hibernate the system"""
        try:
            if "now" in action.lower():
                os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")
                print("System hibernating")
                log("Sytem hibernating")
            else:
                print("Hibernate command not recognized")
                log("Hibernate command not recognized")
        except Exception as e:
            log(f"Error hibernating system: {e}")
            print("Error, check logs")
    
    def open_file(self, filename: str):
        """Search for and open a file"""
        try:
            log(f"Searching for file: {filename}")
            
            # Common directories to search
            search_directories = [
                os.path.expanduser("~"),  # User's home directory
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Music"),
                os.path.expanduser("~/Videos"),
                "C:/",
                "D:/",
                "E:/"
            ]
            
            found_files = []
            
            # Search for files with various extensions
            possible_extensions = ['', '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                                 '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.mp3', 
                                 '.mp4', '.avi', '.mov', '.zip', '.rar', '.exe']
            
            for directory in search_directories:
                if os.path.exists(directory):
                    for ext in possible_extensions:
                        search_pattern = os.path.join(directory, f"*{filename}*{ext}")
                        try:
                            matches = glob.glob(search_pattern, recursive=True)
                            found_files.extend(matches)
                        except:
                            continue
            
            # Remove duplicates and sort by relevance
            found_files = list(set(found_files))
            found_files.sort(key=lambda x: len(x))  # Shorter paths first
            
            if found_files:
                # Take the first (most relevant) match
                file_path = found_files[0]
                log(f"Found file: {file_path}")
                
                # Open the file using the default application
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', file_path])
                
                print(f"Opened file: {os.path.basename(file_path)}")
                log(f"Opened file: {os.path.basename(file_path)}")
            else:
                print(f"File '{filename}' not found in common directories")
                print("Try being more specific with the filename")
                log("File not found")
                
        except Exception as e:
            log(f"Error opening file: {e}")
            print("Error, check logs")
    
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
    agent = VoiceControlAgent(local=LOCAL)
    agent.run()

if __name__ == "__main__":
    main()

