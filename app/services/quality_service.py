from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
from config.logging import get_logger

# Logger for this module
logger = get_logger(__name__)

class QualityStandard(BaseModel):
    standard_id: Optional[str] = None
    name: str
    description: Optional[str]
    threshold: Dict[str, float]

class QualityService:
    def __init__(self):
        self.quality_standards = self._load_quality_standards()

    def _load_quality_standards(self) -> List[QualityStandard]:
        """
        Load quality standards from a JSON file.

        Returns:
            List[QualityStandard]: List of quality standards.
        """
        try:
            if os.path.exists("data/quality_standards.json"):
                with open("data/quality_standards.json", "r") as file:
                    data = json.load(file)
                    return [QualityStandard(**item) for item in data]
            return []
        except Exception as e:
            logger.error(f"Error loading quality standards: {str(e)}", exc_info=True)
            return []

    def _save_quality_standards(self):
        """
        Save quality standards to a JSON file.
        """
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/quality_standards.json", "w") as file:
                json.dump([standard.dict() for standard in self.quality_standards], file, indent=4)
        except Exception as e:
            logger.error(f"Error saving quality standards: {str(e)}", exc_info=True)

    def create_standard(self, standard: QualityStandard) -> QualityStandard:
        """
        Create a new quality standard.

        Args:
            standard (QualityStandard): The quality standard to create.

        Returns:
            QualityStandard: The created quality standard.
        """
        standard.standard_id = f"standard_{len(self.quality_standards) + 1}"
        self.quality_standards.append(standard)
        self._save_quality_standards()
        return standard

    def get_all_standards(self) -> List[QualityStandard]:
        """
        Retrieve all quality standards.

        Returns:
            List[QualityStandard]: List of all quality standards.
        """
        return self.quality_standards

    def update_standard(self, standard_id: str, updated_standard: QualityStandard) -> QualityStandard:
        """
        Update an existing quality standard.

        Args:
            standard_id (str): The ID of the quality standard to update.
            updated_standard (QualityStandard): The updated quality standard.

        Returns:
            QualityStandard: The updated quality standard.
        """
        for standard in self.quality_standards:
            if standard.standard_id == standard_id:
                standard.name = updated_standard.name
                standard.description = updated_standard.description
                standard.threshold = updated_standard.threshold
                self._save_quality_standards()
                return standard
        raise ValueError("Quality standard not found")

    def delete_standard(self, standard_id: str):
        """
        Delete a quality standard by its ID.

        Args:
            standard_id (str): The ID of the quality standard to delete.
        """
        self.quality_standards = [standard for standard in self.quality_standards if standard.standard_id != standard_id]
        self._save_quality_standards()

# Initialize service
quality_service = QualityService()
