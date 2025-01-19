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

# Example usage
if __name__ == "__main__":
    config = load_configuration('config.json')
    send_email_notification("Test Subject", "This is a test email body.", "recipient@example.com")
    
    weather_data = get_weather("London", config['weather_api_key'])
    print(f"Weather in London: {weather_data['weather'][0]['description']}")
    
    greeting = get_greeting()
    print(f"{greeting}! Have a great day.")
