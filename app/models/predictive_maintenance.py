import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime, timedelta
import pickle
import matplotlib.pyplot as plt

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

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        """
        Evaluate the model's performance on test data.

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): Test labels (days to maintenance).

        Returns:
            dict: Evaluation metrics (MAE and R2 score).
        """
        predictions = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        return {
            "mean_absolute_error": round(mae, 2),
            "r2_score": round(r2, 2)
        }

    def plot_feature_importance(self, feature_names: list):
        """
        Plot the importance of each feature used in the model.

        Args:
            feature_names (list): List of feature names.
        """
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]

        # Plot feature importance
        plt.figure(figsize=(10, 6))
        plt.title("Feature Importance")
        plt.bar(range(len(feature_names)), importances[indices], align="center")
        plt.xticks(range(len(feature_names)), [feature_names[i] for i in indices], rotation=90)
        plt.xlabel("Feature")
        plt.ylabel("Importance")
        plt.tight_layout()
        plt.show()
