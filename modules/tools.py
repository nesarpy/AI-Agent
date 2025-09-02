import pyautogui
import time
import webbrowser
import re
import os
import subprocess
import glob
from logger import logger
import keyboard
import random
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pytesseract
import pyautogui
from PIL import Image
import cv2

# Initialize pycaw interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Configure Tesseract path from environment, with a sensible default
tesseract_env_var = os.getenv("TESSERACT_PATH")
if tesseract_env_var and os.path.exists(tesseract_env_var):
    pytesseract.pytesseract.tesseract_cmd = tesseract_env_var
else:
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def click(location):
    """Moves mouse button to location then clicks in a more human like way"""
    pyautogui.moveTo(*location)
    time.sleep(0.1)
    logger.debug("Mouse down")
    pyautogui.mouseDown(*location)
    time.sleep(0.1)
    logger.debug("Mouse up")
    pyautogui.mouseUp(*location)

def Website(url):
    """Opens specified URL in browser"""
    webbrowser.open("https://google.com")
    time.sleep(2)
    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.1)
    pyautogui.write(url)
    pyautogui.press("enter")

def locate(component: str):
    """Locate component on screen using image recognition"""

    if component == "artistcard":
        screenshot = pyautogui.screenshot()
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        
        for i, word in enumerate(data["text"]):
            if word.strip().lower() == "top":
                # Check if "result" follows right after
                if i + 1 < len(data["text"]) and data["text"][i + 1].strip().lower() == "result":
                    x = data["left"][i]
                    y = data["top"][i]
                    
                    # Offset to approximate artist card location
                    target_x = x + 100
                    target_y = y + 200
                    return target_x, target_y
        
        return None
    elif component == "playbutton":
        base_dir = os.path.dirname(os.path.abspath(__file__))
        imgrec_dir = os.path.join(os.path.dirname(base_dir), "imgrec")

        for i in range(1, 5):
            ref_path = os.path.join(imgrec_dir, f"ref{i}.png")
            if not os.path.exists(ref_path):
                continue
            try:
                location = pyautogui.locateOnScreen(ref_path, confidence=0.9, grayscale=True)
            except TypeError:
                location = pyautogui.locateOnScreen(ref_path)
            except Exception as e:
                logger.error(f"locate playbutton error for {ref_path}: {e}")
                continue

            if location is not None:
                return pyautogui.center(location)
        return None
    else:
        return None

def open_application(app_command: str):
    """Open specified application using Windows+R command"""
    try:
        # Open using Windows+R
        pyautogui.hotkey('win', 'r')
        time.sleep(1)
        pyautogui.write(app_command)
        pyautogui.press('enter')
        print(f"Opening: {app_command}")
        logger.info(f"Opening: {app_command}")
    except Exception as e:
        logger.error(f"Error opening {app_command}: {e}")
        print("Error, check logs")

def close_application(app_name: str):
    """Close specified application"""
    try:
        os.system(f"taskkill /f /im {app_name}.exe")
        print(f"Closing {app_name}")
        logger.info(f"Closing {app_name}")
    except Exception as e:
        logger.error(f"Error closing {app_name}: {e}")
        print("Error, check logs")

def web_search(search_term: str):
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
        logger.error(f"Error performing web search: {e}")
        print("Error, check logs")

def volume_control(action: str):
    """Control system volume using pycaw"""
    try:
        action_lower = action.lower()
        
        if "up" in action_lower:
            current = volume.GetMasterVolumeLevelScalar()
            new_level = min(current + 0.1, 1.0)
            volume.SetMasterVolumeLevelScalar(new_level, None)
            print(f"Volume increased to {int(new_level*100)}%")

        elif "down" in action_lower:
            current = volume.GetMasterVolumeLevelScalar()
            new_level = max(current - 0.1, 0.0)
            volume.SetMasterVolumeLevelScalar(new_level, None)
            print(f"Volume decreased to {int(new_level*100)}%")

        elif "mute" in action_lower:
            volume.SetMute(1, None)
            print("Volume muted")

        elif "unmute" in action_lower:
            volume.SetMute(0, None)
            print("Volume unmuted")

        elif "volume" in action_lower:
            # Extract number from action (e.g., "volume 50" -> 50)
            numbers = re.findall(r'\d+', action)
            if numbers:
                target_volume = int(numbers[0])
                if 0 <= target_volume <= 100:
                    volume.SetMasterVolumeLevelScalar(target_volume / 100, None)
                    print(f"Volume set to {target_volume}%")
                else:
                    print("Volume must be between 0 and 100")
            else:
                print("Please specify a volume level (0-100)")

        else:
            print("Volume command not recognized. Use: up, down, mute, unmute, or volume [0-100]")

    except Exception as e:
        logger.error(f"Error controlling volume: {e}")
        print("Error, check logs")

def take_screenshot(filename: str = ""):
    """Take a screenshot"""
    try:
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")
        logger.info(f"Screenshot saved as {filename}")
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        print("Error, check logs")

def powershell(action: str):
    """Run command on command line"""
    try:
        if "now" in action.lower():
            os.system(action)
            print(f"Executing: {action}")
            logger.info(f"Executing via powershell: {action}")
        else:
            print(f"'{action}' not possible")
            logger.warning(f"'{action}' command not recognized")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        print("Error, check logs")

def open_file(filename: str):
    """Search for and open a file"""
    try:
        logger.info(f"Searching for file: {filename}")
        
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
            logger.info(f"Found file: {file_path}")
            
            os.startfile(file_path)
            
            print(f"Opened file: {os.path.basename(file_path)}")
            logger.info(f"Opened file: {os.path.basename(file_path)}")
        else:
            print(f"File '{filename}' not found in common directories")
            print("Try being more specific with the filename")
            logger.warning("File not found")
            
    except Exception as e:
        logger.error(f"Error opening file: {e}")
        print("Error, check logs")

def spotify(playlist: str):
    """Open Spotify and search for the specified artist/playlist"""
    try:
        # Always use search for any artist/playlist
        search_url = f"https://open.spotify.com/search/{playlist.replace(' ', '%20')}"
        print(f"Searching Spotify for: {playlist}")
        logger.info(f"Searching Spotify for: {playlist}")
        Website(search_url)

        # Wait for and click the first result (artist card)
        start_time = time.time()
        location = None
        while location is None and time.time() - start_time < 15:
            location = locate("artistcard")
            time.sleep(0.5)
        if location is not None:
            click(location)
            logger.debug("First click - selecting search result")
        else:
            logger.warning("Artist card not found on screen within timeout")
            return

        time.sleep(1)

        # Wait for and click the play button
        start_time = time.time()
        location = None
        while location is None and time.time() - start_time < 20:
            location = locate("playbutton")
            time.sleep(0.5)
        if location is not None:
            click(location)
            logger.debug("Second click - playing music")
        else:
            logger.warning("Play button not found on screen within timeout")
        
    except Exception as e:
        logger.error(f"Error in Spotify function: {e}")
        print("Error, check logs for more info")