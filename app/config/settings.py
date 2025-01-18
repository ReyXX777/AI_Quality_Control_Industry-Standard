import os
from pydantic import BaseModel, ValidationError
import requests
from typing import Optional

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quality_control.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()

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
    except ValueError as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
