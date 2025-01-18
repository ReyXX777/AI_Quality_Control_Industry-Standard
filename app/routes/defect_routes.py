from fastapi import APIRouter, HTTPException, UploadFile, File
from models.defect_detection import DefectDetectionModel
from services.data_service import preprocess_image
from config.logging import get_logger
from typing import List
import pandas as pd
import os

# Logger for this module
logger = get_logger(__name__)

# Initialize router and model
router = APIRouter()
model = DefectDetectionModel()

# Result storage component
def save_results_to_csv(results: List[dict], output_path: str = "results/defect_detection_results.csv"):
    """
    Save defect detection results to a CSV file.

    Args:
        results (List[dict]): List of defect detection results.
        output_path (str): Path to save the CSV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    logger.info(f"Results saved to {output_path}")

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

@router.post("/detect-batch", summary="Detect defects in a batch of uploaded images")
async def detect_defect_batch(files: List[UploadFile] = File(...)):
    """
    Detect defects in a batch of uploaded images.

    Args:
        files (List[UploadFile]): A list of image files to be inspected.

    Returns:
        dict: Summary of batch defect detection results.
    """
    try:
        results = []
        for file in files:
            # Log the file received
            logger.info(f"Processing file for defect detection: {file.filename}")

            # Preprocess image
            image_tensor = preprocess_image(await file.read())

            # Make prediction
            defect_detected = model.predict(image_tensor)

            result = {
                "filename": file.filename,
                "defect_detected": bool(defect_detected),
                "confidence": defect_detected  # Confidence value can be extended
            }
            results.append(result)

        # Save results to CSV
        save_results_to_csv(results)

        return {
            "total_files": len(files),
            "defects_detected": sum(result["defect_detected"] for result in results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error during batch defect detection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing batch images for defect detection.")
