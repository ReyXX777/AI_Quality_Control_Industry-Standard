from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, List
from config.logging import get_logger
import json
import os

# Logger for this module
logger = get_logger(__name__)

# Initialize router
router = APIRouter()

class ComplianceCheck(BaseModel):
    check_id: Optional[str] = None
    name: str
    description: Optional[str]
    requirements: List[str]
    status: Optional[str] = "Pending"

class ComplianceService:
    def __init__(self):
        self.compliance_checks = self._load_compliance_checks()

    def _load_compliance_checks(self) -> List[ComplianceCheck]:
        """
        Load compliance checks from a JSON file.

        Returns:
            List[ComplianceCheck]: List of compliance checks.
        """
        try:
            if os.path.exists("data/compliance_checks.json"):
                with open("data/compliance_checks.json", "r") as file:
                    data = json.load(file)
                    return [ComplianceCheck(**item) for item in data]
            return []
        except Exception as e:
            logger.error(f"Error loading compliance checks: {str(e)}", exc_info=True)
            return []

    def _save_compliance_checks(self):
        """
        Save compliance checks to a JSON file.
        """
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/compliance_checks.json", "w") as file:
                json.dump([check.dict() for check in self.compliance_checks], file, indent=4)
        except Exception as e:
            logger.error(f"Error saving compliance checks: {str(e)}", exc_info=True)

    def create_compliance_check(self, check: ComplianceCheck):
        """
        Create a new compliance check.

        Args:
            check (ComplianceCheck): The compliance check to create.

        Returns:
            ComplianceCheck: The created compliance check.
        """
        check.check_id = f"check_{len(self.compliance_checks) + 1}"
        self.compliance_checks.append(check)
        self._save_compliance_checks()
        return check

    def get_all_compliance_checks(self) -> List[ComplianceCheck]:
        """
        Retrieve all compliance checks.

        Returns:
            List[ComplianceCheck]: List of all compliance checks.
        """
        return self.compliance_checks

    def update_compliance_check(self, check_id: str, updated_check: ComplianceCheck):
        """
        Update an existing compliance check.

        Args:
            check_id (str): The ID of the compliance check to update.
            updated_check (ComplianceCheck): The updated compliance check.

        Returns:
            ComplianceCheck: The updated compliance check.
        """
        for check in self.compliance_checks:
            if check.check_id == check_id:
                check.name = updated_check.name
                check.description = updated_check.description
                check.requirements = updated_check.requirements
                check.status = updated_check.status
                self._save_compliance_checks()
                return check
        raise HTTPException(status_code=404, detail="Compliance check not found")

    def delete_compliance_check(self, check_id: str):
        """
        Delete a compliance check by its ID.

        Args:
            check_id (str): The ID of the compliance check to delete.
        """
        self.compliance_checks = [check for check in self.compliance_checks if check.check_id != check_id]
        self._save_compliance_checks()

# Initialize service
compliance_service = ComplianceService()

@router.post("/compliance/create", summary="Create a new compliance check")
async def create_compliance_check(check: ComplianceCheck):
    """
    Create a new compliance check.

    Args:
        check (ComplianceCheck): The compliance check to create.

    Returns:
        dict: Confirmation of the created compliance check.
    """
    try:
        logger.info(f"Creating compliance check: {check}")
        result = compliance_service.create_compliance_check(check)
        return {"message": "Compliance check created successfully", "data": result}
    except Exception as e:
        logger.error(f"Error creating compliance check: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create compliance check.")

@router.get("/compliance/list", summary="List all compliance checks")
async def list_compliance_checks():
    """
    Retrieve all compliance checks.

    Returns:
        list: List of all compliance checks.
    """
    try:
        logger.info("Fetching all compliance checks")
        checks = compliance_service.get_all_compliance_checks()
        return {"data": checks}
    except Exception as e:
        logger.error(f"Error listing compliance checks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch compliance checks.")

@router.put("/compliance/update/{check_id}", summary="Update an existing compliance check")
async def update_compliance_check(check_id: str, check: ComplianceCheck):
    """
    Update an existing compliance check.

    Args:
        check_id (str): The ID of the compliance check to update.
        check (ComplianceCheck): The updated compliance check.

    Returns:
        dict: Confirmation of the update.
    """
    try:
        logger.info(f"Updating compliance check {check_id} with data: {check}")
        result = compliance_service.update_compliance_check(check_id, check)
        return {"message": "Compliance check updated successfully", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating compliance check {check_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update compliance check.")

@router.delete("/compliance/delete/{check_id}", summary="Delete a compliance check")
async def delete_compliance_check(check_id: str):
    """
    Delete a compliance check by its ID.

    Args:
        check_id (str): The ID of the compliance check to delete.

    Returns:
        dict: Confirmation of the deletion.
    """
    try:
        logger.info(f"Deleting compliance check with ID: {check_id}")
        compliance_service.delete_compliance_check(check_id)
        return {"message": "Compliance check deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting compliance check {check_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete compliance check.")
