from fastapi import APIRouter, HTTPException, Query
from models.predictive_maintenance import PredictiveMaintenanceModel
from services.data_service import fetch_maintenance_data
from config.logging import get_logger

# Logger for this module
logger = get_logger(__name__)

# Initialize router and model
router = APIRouter()
model = PredictiveMaintenanceModel()

@router.get("/predict", summary="Predict maintenance needs for equipment")
async def predict_maintenance(
    equipment_id: str = Query(..., description="Unique identifier for the equipment")
):
    """
    Predict maintenance needs for the specified equipment.

    Args:
        equipment_id (str): The unique identifier for the equipment.

    Returns:
        dict: Predicted maintenance details including next maintenance date and risk score.
    """
    try:
        # Log the request
        logger.info(f"Received maintenance prediction request for equipment_id: {equipment_id}")

        # Fetch data for the specified equipment
        data = fetch_maintenance_data(equipment_id)
        if not data:
            logger.warning(f"No data found for equipment_id: {equipment_id}")
            raise HTTPException(status_code=404, detail="Equipment data not found")

        # Make prediction
        prediction = model.predict(data)
        logger.info(f"Prediction result for equipment_id {equipment_id}: {prediction}")

        return {
            "equipment_id": equipment_id,
            "next_maintenance_date": prediction["next_date"],
            "risk_score": prediction["risk_score"]
        }

    except Exception as e:
        logger.error(f"Error during maintenance prediction for equipment_id {equipment_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing maintenance prediction request.")
