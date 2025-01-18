from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, validator
from typing import Optional, Dict, List
from services.quality_service import QualityService
from config.logging import get_logger
import csv
import os

# Logger for this module
logger = get_logger(__name__)

# Initialize router and service
router = APIRouter()
quality_service = QualityService()

class QualityStandard(BaseModel):
    standard_id: Optional[str] = None
    name: str
    description: Optional[str]
    threshold: Dict[str, float]

    @validator('threshold')
    def validate_threshold(cls, value):
        """
        Validate that threshold values are between 0 and 1.
        """
        for key, val in value.items():
            if not 0 <= val <= 1:
                raise ValueError(f"Threshold value for '{key}' must be between 0 and 1")
        return value

@router.post("/create", summary="Create a new quality standard")
async def create_quality_standard(standard: QualityStandard):
    """
    Create a new quality standard.

    Args:
        standard (QualityStandard): Details of the quality standard to be created.

    Returns:
        dict: Confirmation of the created quality standard.
    """
    try:
        logger.info(f"Creating quality standard: {standard}")
        result = quality_service.create_standard(standard.dict())
        return {"message": "Quality standard created successfully", "data": result}
    except Exception as e:
        logger.error(f"Error creating quality standard: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create quality standard.")

@router.get("/list", summary="List all quality standards")
async def list_quality_standards():
    """
    Retrieve all defined quality standards.

    Returns:
        list: List of all quality standards.
    """
    try:
        logger.info("Fetching all quality standards")
        standards = quality_service.get_all_standards()
        return {"data": standards}
    except Exception as e:
        logger.error(f"Error listing quality standards: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch quality standards.")

@router.put("/update/{standard_id}", summary="Update an existing quality standard")
async def update_quality_standard(standard_id: str, standard: QualityStandard):
    """
    Update an existing quality standard.

    Args:
        standard_id (str): ID of the quality standard to be updated.
        standard (QualityStandard): Updated details of the quality standard.

    Returns:
        dict: Confirmation of the update.
    """
    try:
        logger.info(f"Updating quality standard {standard_id} with data: {standard}")
        result = quality_service.update_standard(standard_id, standard.dict())
        return {"message": "Quality standard updated successfully", "data": result}
    except Exception as e:
        logger.error(f"Error updating quality standard {standard_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update quality standard.")

@router.delete("/delete/{standard_id}", summary="Delete a quality standard")
async def delete_quality_standard(standard_id: str):
    """
    Delete a quality standard by its ID.

    Args:
        standard_id (str): ID of the quality standard to delete.

    Returns:
        dict: Confirmation of the deletion.
    """
    try:
        logger.info(f"Deleting quality standard with ID: {standard_id}")
        quality_service.delete_standard(standard_id)
        return {"message": "Quality standard deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting quality standard {standard_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete quality standard.")

@router.post("/export", summary="Export quality standards to a CSV file")
async def export_quality_standards():
    """
    Export all quality standards to a CSV file.

    Returns:
        dict: Confirmation of the export and file path.
    """
    try:
        logger.info("Exporting quality standards to CSV")
        standards = quality_service.get_all_standards()
        if not standards:
            raise HTTPException(status_code=404, detail="No quality standards found to export")

        # Ensure the export directory exists
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)

        # Define the CSV file path
        file_path = os.path.join(export_dir, "quality_standards.csv")

        # Write standards to CSV
        with open(file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["standard_id", "name", "description", "threshold"])
            writer.writeheader()
            for standard in standards:
                writer.writerow(standard)

        logger.info(f"Quality standards exported to {file_path}")
        return {"message": "Quality standards exported successfully", "file_path": file_path}
    except Exception as e:
        logger.error(f"Error exporting quality standards: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export quality standards.")
