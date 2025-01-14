from fastapi import APIRouter, HTTPException
from models.predictive_maintenance import PredictiveMaintenanceModel
from services.data_service import fetch_maintenance_data

router = APIRouter()
model = PredictiveMaintenanceModel()

@router.get("/predict")
async def predict_maintenance(equipment_id: str):
    """
    Predict the maintenance needs for a specific equipment ID.

    Args:
        equipment_id (str): The unique identifier for the equipment.

    Returns:
        dict: Predicted maintenance date and risk score.
    """
    try:
        # Fetch equipment-specific data
        data = fetch_maintenance_data(equipment_id)
        if not data:
            raise HTTPException(status_code=404, detail="Equipment data not found")

        # Generate predictions
        prediction = model.predict(data)
        return {
            "equipment_id": equipment_id,
            "next_maintenance_date": prediction["next_date"],
            "risk_score": prediction["risk_score"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting maintenance: {str(e)}")
