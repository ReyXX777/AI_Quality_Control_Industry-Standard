import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(LOG_DIR, "application.log")

# Define log formatting
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create a rotating file handler
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)  # 5 MB per file
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Default log level
    handlers=[file_handler, console_handler]
)

# Function to get a logger for a specific module
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
