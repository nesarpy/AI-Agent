import logging
from logging.handlers import TimedRotatingFileHandler
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("ai_agent")
    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(
        "logs/log.txt", when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    handler.suffix = "%Y-%m-%d"
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)

    if not logger.handlers:  # avoid duplicate handlers on reload
        logger.addHandler(handler)

    return logger

# Expose a global logger instance
logger = setup_logger()