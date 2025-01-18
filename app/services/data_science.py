from PIL import Image, UnidentifiedImageError
from torchvision import transforms
import io
import logging

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
