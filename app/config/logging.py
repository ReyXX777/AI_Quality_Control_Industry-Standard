import logging
import os
from logging.handlers import RotatingFileHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
from datetime import datetime

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

# Email notification component
def send_email_notification(subject: str, body: str, to_email: str):
    try:
        # Load email configuration
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        
        from_email = config['email']['from_email']
        smtp_server = config['email']['smtp_server']
        smtp_port = config['email']['smtp_port']
        smtp_username = config['email']['smtp_username']
        smtp_password = config['email']['smtp_password']

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logger = get_logger(__name__)
        logger.info(f"Email notification sent to {to_email}")

    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to send email notification: {e}")

# Configuration management component
def load_configuration(config_file: str) -> dict:
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        logger = get_logger(__name__)
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to load configuration: {e}")
        return {}

# Weather API component
def get_weather(city: str, api_key: str) -> dict:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        logger = get_logger(__name__)
        logger.info(f"Weather data fetched for {city}")
        return weather_data
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to fetch weather data: {e}")
        return {}

# Time-based greeting component
def get_greeting() -> str:
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

# New Component: File Backup
def backup_file(file_path: str, backup_dir: str):
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        file_name = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, file_name)
        
        with open(file_path, 'rb') as src_file, open(backup_path, 'wb') as dest_file:
            dest_file.write(src_file.read())
        
        logger = get_logger(__name__)
        logger.info(f"File {file_name} backed up to {backup_dir}")
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to backup file: {e}")

# New Component: System Information
def get_system_info() -> dict:
    try:
        import platform
        system_info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
        logger = get_logger(__name__)
        logger.info("System information fetched successfully")
        return system_info
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to fetch system information: {e}")
        return {}

# New Component: Disk Usage
def get_disk_usage(path: str) -> dict:
    try:
        disk_usage = os.statvfs(path)
        total_space = disk_usage.f_frsize * disk_usage.f_blocks
        used_space = total_space - (disk_usage.f_bavail * disk_usage.f_frsize)
        usage_percentage = (used_space / total_space) * 100
        disk_info = {
            "total_space": total_space,
            "used_space": used_space,
            "usage_percentage": usage_percentage
        }
        logger = get_logger(__name__)
        logger.info(f"Disk usage fetched for {path}")
        return disk_info
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to fetch disk usage: {e}")
        return {}

# New Component: Network Check
def check_network_connection() -> bool:
    try:
        response = requests.get("https://www.google.com", timeout=5)
        logger = get_logger(__name__)
        logger.info("Network connection is active")
        return True
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Network connection check failed: {e}")
        return False

# New Component: Directory Listing
def list_directory_contents(directory: str) -> list:
    try:
        contents = os.listdir(directory)
        logger = get_logger(__name__)
        logger.info(f"Directory contents listed for {directory}")
        return contents
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to list directory contents: {e}")
        return []

# New Component: File Size Check
def get_file_size(file_path: str) -> int:
    try:
        size = os.path.getsize(file_path)
        logger = get_logger(__name__)
        logger.info(f"File size fetched for {file_path}")
        return size
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to get file size: {e}")
        return -1

# Example usage
if __name__ == "__main__":
    config = load_configuration('config.json')
    send_email_notification("Test Subject", "This is a test email body.", "recipient@example.com")
    
    weather_data = get_weather("London", config['weather_api_key'])
    print(f"Weather in London: {weather_data['weather'][0]['description']}")
    
    greeting = get_greeting()
    print(f"{greeting}! Have a great day.")
    
    backup_file('config.json', 'backups')
    
    system_info = get_system_info()
    print(f"System Info: {system_info}")
    
    disk_usage = get_disk_usage('/')
    print(f"Disk Usage: {disk_usage}")
    
    network_status = check_network_connection()
    print(f"Network Status: {'Connected' if network_status else 'Disconnected'}")
    
    directory_contents = list_directory_contents('.')
    print(f"Directory Contents: {directory_contents}")
    
    file_size = get_file_size('config.json')
    print(f"File Size of config.json: {file_size} bytes")
