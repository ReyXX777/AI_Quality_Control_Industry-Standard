from fastapi import APIRouter, HTTPException, UploadFile, File
from models.defect_detection import DefectDetectionModel
from services.data_service import preprocess_image
from config.logging import get_logger

# Logger for this module
logger = get_logger(__name__)

# Initialize router and model
router = APIRouter()
model = DefectDetectionModel()

@router.post("/detect", summary="Detect defects in an uploaded image")
async def detect_defect(file: UploadFile = File(...)):
    """
    Detect defects in the uploaded image.

    Args:
        file (UploadFile): An image file containing a product to be inspected.

    Returns:
        dict: Result of defect detection.
    """
    try:
        # Log the file received
        logger.info(f"Received file for defect detection: {file.filename}")

        # Preprocess image
        image_tensor = preprocess_image(await file.read())

        # Make prediction
        defect_detected = model.predict(image_tensor)

        result = {
            "filename": file.filename,
            "defect_detected": bool(defect_detected),
            "confidence": defect_detected  # Confidence value can be extended
        }

        logger.info(f"Defect detection result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error during defect detection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing the image for defect detection.")
