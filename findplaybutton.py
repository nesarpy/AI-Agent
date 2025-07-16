import pyautogui

# finds playbutton coords
def locateButton():
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
            print(f"Found playbutton using {image}")
            return x, y
    
    # if no image is matched, return None
    return location