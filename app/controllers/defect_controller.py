from fastapi import APIRouter, UploadFile, HTTPException
from models.defect_detection import DefectDetectionModel
from services.data_service import preprocess_image
import logging
from typing import List
import shutil
import os

router = APIRouter()
model = DefectDetectionModel()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File validation component
ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/jpg"]

def validate_file_type(file: UploadFile) -> bool:
    """Validate if the uploaded file is of an allowed type."""
    return file.content_type in ALLOWED_FILE_TYPES

# Logging component
def log_prediction(file_name: str, prediction: bool):
    """Log the prediction result for auditing purposes."""
    logger.info(f"File: {file_name}, Defect Detected: {prediction}")

# File storage component
def save_uploaded_file(file: UploadFile, directory: str = "uploads"):
    """Save the uploaded file to a specified directory."""
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"File saved to {file_path}")
    return file_path

# Notification component
def send_notification(message: str):
    """Send a notification (e.g., to a logging system or external service)."""
    logger.info(f"Notification: {message}")

# New Component: File Cleanup
def cleanup_files(directory: str = "uploads", max_files: int = 10):
    """Clean up old files in the directory to prevent storage overflow."""
    try:
        files = os.listdir(directory)
        if len(files) > max_files:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))
            for file in files[:-max_files]:
                os.remove(os.path.join(directory, file))
                logger.info(f"Deleted old file: {file}")
    except Exception as e:
        logger.error(f"Failed to clean up files: {e}")

# New Component: Prediction Analytics
def log_analytics(file_name: str, prediction: bool):
    """Log analytics data for further analysis."""
    try:
        analytics_data = {
            "file_name": file_name,
            "prediction": prediction,
            "timestamp": logging.Formatter("%(asctime)s").format(logging.LogRecord(
                name=__name__, level=logging.INFO, pathname=__file__, lineno=0,
                msg="", args=(), exc_info=None
            ))
        }
        with open("analytics.log", "a") as analytics_file:
            analytics_file.write(f"{analytics_data}\n")
        logger.info(f"Analytics logged for {file_name}")
    except Exception as e:
        logger.error(f"Failed to log analytics: {e}")

@router.post("/detect")
async def detect_defect(file: UploadFile):
    # Validate file type
    if not validate_file_type(file):
        raise HTTPException(status_code=400, detail="File type not allowed. Only JPEG, PNG, and JPG are supported.")

    try:
        # Save the uploaded file
        file_path = save_uploaded_file(file)

        # Preprocess and predict
        image_tensor = preprocess_image(await file.read())
        prediction = model.predict(image_tensor)
        result = bool(prediction)

        # Log the prediction
        log_prediction(file.filename, result)

        # Log analytics
        log_analytics(file.filename, result)

        # Clean up old files
        cleanup_files()

        # Send a notification
        send_notification(f"Defect detection completed for {file.filename}. Result: {result}")

        return {"defect_detected": result}
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")
