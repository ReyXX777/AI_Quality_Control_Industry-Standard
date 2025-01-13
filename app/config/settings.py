import os

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quality_control.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
