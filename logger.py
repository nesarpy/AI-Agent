from datetime import datetime
import os

now = datetime.now()

def log(text):
    tdy = now.date()
    time = now.time().replace(microsecond=0)
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/log-{str(tdy)}.txt", "a") as f:
        f.write(str(time) + " | " + str(text) + "\n")