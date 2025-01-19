from fastapi import APIRouter, HTTPException
from models.predictive_maintenance import PredictiveMaintenanceModel
from services.data_service import fetch_maintenance_data
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from functools import lru_cache
import logging

router = APIRouter()
model = PredictiveMaintenanceModel()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data caching component
@lru_cache(maxsize=100)
def cached_fetch_maintenance_data(equipment_id: str):
    """
    Cache equipment data to reduce redundant API calls.
    """
    return fetch_maintenance_data(equipment_id)

# Email alert component
def send_maintenance_alert(equipment_id: str, next_maintenance_date: str, risk_score: float, recipient: str):
    """
    Send an email alert for predicted maintenance.
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
        logger.info(f"Maintenance alert sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email alert: {str(e)}")

# Logging component for predictions
def log_prediction(equipment_id: str, next_maintenance_date: str, risk_score: float):
    """
    Log the prediction details for auditing and monitoring.
    """
    logger.info(
        f"Prediction for Equipment {equipment_id}: "
        f"Next Maintenance Date: {next_maintenance_date}, Risk Score: {risk_score}"
    )

# Notification component for system alerts
def send_system_notification(message: str):
    """
    Send a system-wide notification for critical events.
    """
    logger.warning(f"System Notification: {message}")

@router.get("/predict")
async def predict_maintenance(equipment_id: str, alert_recipient: str = None):
    """
    Predict the maintenance needs for a specific equipment ID.

    Args:
        equipment_id (str): The unique identifier for the equipment.
        alert_recipient (str, optional): Email address to send maintenance alerts.

    Returns:
        dict: Predicted maintenance date and risk score.
    """
    try:
        # Fetch equipment-specific data with caching
        data = cached_fetch_maintenance_data(equipment_id)
        if not data:
            raise HTTPException(status_code=404, detail="Equipment data not found")

        # Generate predictions
        prediction = model.predict(data)
        result = {
            "equipment_id": equipment_id,
            "next_maintenance_date": prediction["next_date"],
            "risk_score": prediction["risk_score"],
        }

        # Log the prediction
        log_prediction(equipment_id, prediction["next_date"], prediction["risk_score"])

        # Send email alert if recipient is provided
        if alert_recipient:
            send_maintenance_alert(equipment_id, prediction["next_date"], prediction["risk_score"], alert_recipient)

        # Send system notification for high-risk predictions
        if prediction["risk_score"] > 0.8:
            send_system_notification(
                f"High-risk maintenance predicted for Equipment {equipment_id}. Risk Score: {prediction['risk_score']}"
            )

        return result
    except Exception as e:
        logger.error(f"Error predicting maintenance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error predicting maintenance: {str(e)}")
