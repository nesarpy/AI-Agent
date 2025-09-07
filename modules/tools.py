import re
import os
import time
import webbrowser
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui
from logger import logger
import pytesseract
from PIL import Image  # noqa: F401 (imported for completeness in case of future use)
import cv2  # noqa: F401 (imported for completeness in case of future use)

# Initialize pycaw interface for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def click(location):
    """Move mouse to location and click."""
    try:
        pyautogui.moveTo(*location)
        time.sleep(0.1)
        pyautogui.mouseDown(*location)
        time.sleep(0.1)
        pyautogui.mouseUp(*location)
    except Exception as e:
        logger.error(f"Error clicking at {location}: {e}")

def locate(component: str):
    """Locate component on screen using OCR or image matching."""
    try:
        if component == "artistcard":
            screenshot = pyautogui.screenshot()
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            for i, word in enumerate(data.get("text", [])):
                if word and word.strip().lower() == "top":
                    if i + 1 < len(data["text"]) and str(data["text"][i + 1]).strip().lower() == "result":
                        x = data["left"][i]
                        y = data["top"][i]
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
    except Exception as e:
        logger.error(f"Error in locate('{component}'): {e}")
        return None

def volume_control(target: int):
    """Set system volume to a value between 0 and 100 using pycaw."""
    try:
        if not isinstance(target, (int, float)):
            print("Volume must be a number between 0 and 100")
            return

        if 0 <= target <= 100:
            volume.SetMasterVolumeLevelScalar(target / 100, None)
            print(f"Volume set to {target}%")
        else:
            print("Volume must be between 0 and 100")
    except Exception as e:
        logger.error(f"Error controlling volume: {e}")
        print("Error, check logs")

    except Exception as e:
        logger.error(f"Error controlling volume: {e}")
        print("Error, check logs")

def type_text(text: str):
    """Type the given text with a small delay between characters."""
    try:
        pyautogui.write(text, interval=0.05)
    except Exception as e:
        logger.error(f"Error typing text: {e}")

def shortcut(keys: str):
    """Execute a keyboard shortcut or single key press.

    Accepts strings like:
    - "win" (Windows key menu)
    - "enter", "esc", "tab"
    - "win+r", "ctrl+shift+esc", "alt+f4"
    Multiple keys are separated by '+'.
    """
    try:
        normalized = keys.strip().lower()
        if "+" in normalized:
            parts = [p.strip() for p in normalized.split("+") if p.strip()]
            pyautogui.hotkey(*parts)
        else:
            pyautogui.press(normalized)
    except Exception as e:
        logger.error(f"Error executing shortcut '{keys}': {e}")

def Website(url: str):
    """Open a specific website in Brave via keyboard automation."""
    try:
        # Open Google in default browser
        webbrowser.open("https://www.google.com")
        time.sleep(1.5)
        # Focus address bar and navigate to target URL
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.1)
        pyautogui.write(url)
        pyautogui.press("enter")
    except Exception as e:
        logger.error(f"Website error for '{url}': {e}")

def play(app: str):
    """In Spotify, click the artist card then the play button. Assumes Spotify is open."""
    try:
        start_time = time.time()
        location_point = None
        while location_point is None and time.time() - start_time < 15:
            location_point = locate("artistcard")
            time.sleep(0.5)
        if location_point is not None:
            click(location_point)
        else:
            logger.warning("Artist card not found on screen within timeout")

        time.sleep(1)

        start_time = time.time()
        location_point = None
        while location_point is None and time.time() - start_time < 20:
            location_point = locate("playbutton")
            time.sleep(0.5)
        if location_point is not None:
            click(location_point)
        else:
            logger.warning("Play button not found on screen within timeout")
            return
    except Exception as e:
        logger.error(f"Error in Spotify play function: {e}")