import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import pickle

class PredictiveMaintenanceModel:
    """
    Predictive maintenance model using a Random Forest Regressor.
    Predicts the number of days until maintenance is required and the associated risk score.
    """

    def __init__(self):
        # Initialize or load the pre-trained Random Forest model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        try:
            with open("models/maintenance_model.pkl", "rb") as f:
                self.model = pickle.load(f)
        except FileNotFoundError:
            print("Pre-trained model not found. Using an untrained model.")

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train the predictive maintenance model.

        Args:
            X_train (np.ndarray): Training features.
            y_train (np.ndarray): Training labels (days to maintenance).
        """
        self.model.fit(X_train, y_train)
        with open("models/maintenance_model.pkl", "wb") as f:
            pickle.dump(self.model, f)

    def predict(self, data: np.ndarray):
        """
        Predict maintenance needs based on input data.

        Args:
            data (np.ndarray): Feature data for prediction.

        Returns:
            dict: Predicted next maintenance date and risk score.
        """
        # Predict days to maintenance
        days_to_maintenance = self.model.predict(data)[0]

        # Calculate risk score (arbitrary example: higher days = lower risk)
        risk_score = max(0, 100 - days_to_maintenance * 10)

        # Determine next maintenance date
        next_date = datetime.now() + timedelta(days=int(days_to_maintenance))

        return {
            "next_date": next_date.strftime("%Y-%m-%d"),
            "risk_score": round(risk_score, 2)
        }
