import pyautogui
import time

print("Mouse Coordinate Tracker")
print("Press Enter to log current mouse position")
print("Press Ctrl+C to exit")
print("-" * 40)

try:
    while True:
        input()  # Wait for Enter key
        x, y = pyautogui.position()
        print(f"Mouse position: ({x}, {y})")
        
except KeyboardInterrupt:
    print("\nExiting...") 