from PIL import Image, UnidentifiedImageError
from torchvision import transforms
import io
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_image(image_data: bytes) -> bool:
    """
    Validate if the provided image data is a valid image.

    Args:
        image_data (bytes): The image data to validate.

    Returns:
        bool: True if the image is valid, otherwise False.
    """
    try:
        Image.open(io.BytesIO(image_data)).verify()
        return True
    except (UnidentifiedImageError, Exception) as e:
        logger.error(f"Invalid image data: {str(e)}")
        return False

def preprocess_image(image_data: bytes):
    """
    Preprocess the image data for model input.

    Args:
        image_data (bytes): The image data to preprocess.

    Returns:
        torch.Tensor: Preprocessed image tensor with batch dimension.
    """
    if not validate_image(image_data):
        raise ValueError("Invalid image data provided")

    try:
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize for pretrained models
        ])
        return transform(image).unsqueeze(0)  # Add batch dimension
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to preprocess image: {str(e)}")

# Image Storage Component
def save_uploaded_image(image_data: bytes, directory: str = "uploads"):
    """
    Save the uploaded image to a specified directory.

    Args:
        image_data (bytes): The image data to save.
        directory (str): Directory to save the image.

    Returns:
        str: Path to the saved image.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(directory, f"image_{timestamp}.jpg")
        with open(file_path, "wb") as file:
            file.write(image_data)
        logger.info(f"Image saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to save image: {str(e)}")

# Image Metadata Logging Component
def log_image_metadata(image_data: bytes, metadata: dict):
    """
    Log metadata about the uploaded image.

    Args:
        image_data (bytes): The image data.
        metadata (dict): Metadata to log (e.g., filename, size, etc.).
    """
    try:
        os.makedirs("logs/images", exist_ok=True)
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_size": len(image_data),
            **metadata
        }
        with open("logs/images/image_metadata.log", "a") as log_file:
            log_file.write(json.dumps(log_entry) + "\n")
        logger.info(f"Image metadata logged: {log_entry}")
    except Exception as e:
        logger.error(f"Error logging image metadata: {str(e)}", exc_info=True)
