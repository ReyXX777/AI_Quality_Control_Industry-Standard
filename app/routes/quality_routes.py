from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict
from services.quality_service import QualityService
from config.logging import get_logger

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
