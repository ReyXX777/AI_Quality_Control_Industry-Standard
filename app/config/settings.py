import os
from pydantic import BaseModel, ValidationError
import requests
from typing import Optional
import logging

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quality_control.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# API Client component
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(self, endpoint: str, params: Optional[dict] = None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

# Data Validation component
class UserData(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None

def validate_user_data(data: dict):
    try:
        user = UserData(**data)
        return user
    except ValidationError as e:
        raise ValueError(f"Invalid user data: {e}")

# File Handling component
def save_to_file(filename: str, data: str):
    try:
        with open(filename, "w") as file:
            file.write(data)
        logger.info(f"Data successfully saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save data to file: {e}")

# Notification component
def send_notification(message: str):
    try:
        # Simulate sending a notification (e.g., to a logging system or external service)
        logger.info(f"Notification sent: {message}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

# New Component: Data Encryption
def encrypt_data(data: str, key: str) -> str:
    try:
        from cryptography.fernet import Fernet
        cipher_suite = Fernet(key.encode())
        encrypted_data = cipher_suite.encrypt(data.encode())
        logger.info("Data encrypted successfully")
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Failed to encrypt data: {e}")
        raise

# New Component: Data Decryption
def decrypt_data(encrypted_data: str, key: str) -> str:
    try:
        from cryptography.fernet import Fernet
        cipher_suite = Fernet(key.encode())
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        logger.info("Data decrypted successfully")
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Failed to decrypt data: {e}")
        raise

# Example usage
if __name__ == "__main__":
    api_client = APIClient(base_url="https://api.example.com")
    user_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30
    }

    try:
        validated_data = validate_user_data(user_data)
        print("User data is valid:", validated_data)
        response = api_client.post("users", data=validated_data.dict())
        print("API response:", response)

        # Save API response to a file
        save_to_file("user_response.txt", str(response))

        # Encrypt and decrypt data
        encryption_key = "your-encryption-key-here"
        encrypted_response = encrypt_data(str(response), encryption_key)
        print("Encrypted response:", encrypted_response)
        decrypted_response = decrypt_data(encrypted_response, encryption_key)
        print("Decrypted response:", decrypted_response)

        # Send a notification
        send_notification("User data processed successfully")
    except ValueError as e:
        logger.error(e)
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
