from fastapi import APIRouter, HTTPException, Query
from models.predictive_maintenance import PredictiveMaintenanceModel
from services.data_service import fetch_maintenance_data
from config.logging import get_logger
from functools import lru_cache
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Logger for this module
logger = get_logger(__name__)

# Initialize router and model
router = APIRouter()
model = PredictiveMaintenanceModel()

# Prediction caching component
@lru_cache(maxsize=100)
def cached_predict_maintenance(equipment_id: str):
    """
    Cache maintenance predictions to reduce redundant computations.

    Args:
        equipment_id (str): The unique identifier for the equipment.

    Returns:
        dict: Predicted maintenance details.
    """
    data = fetch_maintenance_data(equipment_id)
    if not data:
        raise HTTPException(status_code=404, detail="Equipment data not found")
    return model.predict(data)

# Alert notification component
def send_maintenance_alert(equipment_id: str, next_maintenance_date: str, risk_score: float, recipient: str):
    """
    Send an email alert for predicted maintenance.

    Args:
        equipment_id (str): The unique identifier for the equipment.
        next_maintenance_date (str): Predicted next maintenance date.
        risk_score (float): Predicted risk score.
        recipient (str): Email address of the recipient.
    """
    try:
        subject = f"Maintenance Alert for Equipment {equipment_id}"
        body = (
            f"Maintenance is predicted for equipment {equipment_id}.\n"
            f"Next Maintenance Date: {next_maintenance_date}\n"
            f"Risk Score: {risk_score}\n"
            "Please schedule maintenance accordingly."
        )
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "noreply@maintenance.com"
        msg["To"] = recipient

        with smtplib.SMTP("smtp.example.com", 587) as server:
            server.starttls()
            server.login("user@example.com", "password")
            server.sendmail("noreply@maintenance.com", recipient, msg.as_string())
        logger.info(f"Maintenance alert sent to {recipient} for equipment_id {equipment_id}")
    except Exception as e:
        logger.error(f"Failed to send maintenance alert for equipment_id {equipment_id}: {str(e)}")

@router.get("/predict", summary="Predict maintenance needs for equipment")
async def predict_maintenance(
    equipment_id: str = Query(..., description="Unique identifier for the equipment"),
    alert_recipient: str = Query(None, description="Email address to send maintenance alerts")
):
    """
    Predict maintenance needs for the specified equipment.

    Args:
        equipment_id (str): The unique identifier for the equipment.
        alert_recipient (str, optional): Email address to send maintenance alerts.

    Returns:
        dict: Predicted maintenance details including next maintenance date and risk score.
    """
    try:
        # Log the request
        logger.info(f"Received maintenance prediction request for equipment_id: {equipment_id}")

        # Fetch data and make prediction (with caching)
        prediction = cached_predict_maintenance(equipment_id)
        logger.info(f"Prediction result for equipment_id {equipment_id}: {prediction}")

        # Send alert if recipient is provided
        if alert_recipient:
            send_maintenance_alert(equipment_id, prediction["next_date"], prediction["risk_score"], alert_recipient)

        return {
            "equipment_id": equipment_id,
            "next_maintenance_date": prediction["next_date"],
            "risk_score": prediction["risk_score"]
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during maintenance prediction for equipment_id {equipment_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing maintenance prediction request.")
