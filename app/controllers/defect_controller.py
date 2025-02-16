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

# New Component: File Size Check
def check_file_size(file: UploadFile, max_size_mb: int = 10) -> bool:
    """Check if the file size is within the allowed limit."""
    file.file.seek(0, 2)  # Move to the end of the file
    file_size = file.file.tell()  # Get the file size in bytes
    file.file.seek(0)  # Reset file pointer to the beginning
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        logger.warning(f"File {file.filename} exceeds size limit: {file_size} bytes")
        return False
    return True

# New Component: File Type Conversion
def convert_image_format(file_path: str, target_format: str = "png"):
    """Convert an image file to a specified format."""
    try:
        from PIL import Image
        img = Image.open(file_path)
        new_file_path = file_path.rsplit(".", 1)[0] + f".{target_format}"
        img.save(new_file_path, target_format.upper())
        logger.info(f"File converted to {target_format}: {new_file_path}")
        return new_file_path
    except Exception as e:
        logger.error(f"Failed to convert file format: {e}")
        return None

# New Component: Batch Processing
def process_batch_files(files: List[UploadFile]):
    """Process multiple files in a batch."""
    results = []
    for file in files:
        try:
            if not validate_file_type(file):
                logger.warning(f"Skipping invalid file type: {file.filename}")
                continue
            if not check_file_size(file):
                logger.warning(f"Skipping oversized file: {file.filename}")
                continue

            file_path = save_uploaded_file(file)
            image_tensor = preprocess_image(file.file.read())
            prediction = model.predict(image_tensor)
            result = bool(prediction)

            log_prediction(file.filename, result)
            log_analytics(file.filename, result)
            results.append({"file_name": file.filename, "defect_detected": result})
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            results.append({"file_name": file.filename, "error": str(e)})
    return results

@router.post("/detect")
async def detect_defect(file: UploadFile):
    # Validate file type
    if not validate_file_type(file):
        raise HTTPException(status_code=400, detail="File type not allowed. Only JPEG, PNG, and JPG are supported.")

    # Validate file size
    if not check_file_size(file):
        raise HTTPException(status_code=400, detail="File size exceeds the allowed limit (10MB).")

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

@router.post("/batch-detect")
async def batch_detect_defect(files: List[UploadFile]):
    try:
        results = process_batch_files(files)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error during batch processing: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during batch processing.")
