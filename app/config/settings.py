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

# New Component: File Backup
def backup_file(file_path: str, backup_dir: str):
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        file_name = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, file_name)
        
        with open(file_path, 'rb') as src_file, open(backup_path, 'wb') as dest_file:
            dest_file.write(src_file.read())
        
        logger.info(f"File {file_name} backed up to {backup_dir}")
    except Exception as e:
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
        logger.info("System information fetched successfully")
        return system_info
    except Exception as e:
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
        logger.info(f"Disk usage fetched for {path}")
        return disk_info
    except Exception as e:
        logger.error(f"Failed to fetch disk usage: {e}")
        return {}

# New Component: Network Check
def check_network_connection() -> bool:
    try:
        response = requests.get("https://www.google.com", timeout=5)
        logger.info("Network connection is active")
        return True
    except Exception as e:
        logger.error(f"Network connection check failed: {e}")
        return False

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

        # Backup file
        backup_file("user_response.txt", "backups")

        # Get system information
        system_info = get_system_info()
        print("System Info:", system_info)

        # Get disk usage
        disk_usage = get_disk_usage('/')
        print("Disk Usage:", disk_usage)

        # Check network connection
        network_status = check_network_connection()
        print("Network Status:", "Connected" if network_status else "Disconnected")

        # Send a notification
        send_notification("User data processed successfully")
    except ValueError as e:
        logger.error(e)
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
