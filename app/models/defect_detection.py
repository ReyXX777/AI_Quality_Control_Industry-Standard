import torch
from torchvision import models, transforms
from torch.utils.data import DataLoader
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DefectDetectionModel:
    def __init__(self):
        self.model = models.resnet18(pretrained=True)  # Pretrained ResNet
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 2)  # Binary classification
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def predict(self, image_tensor):
        self.model.eval()
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            output = self.model(image_tensor)
        return torch.argmax(output, dim=1).item()

    def save_model(self, path: str):
        """
        Save the model to a specified path.

        Args:
            path (str): Path to save the model.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.model.state_dict(), path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """
        Load the model from a specified path.

        Args:
            path (str): Path to load the model from.
        """
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            logger.info(f"Model loaded from {path}")
        else:
            raise FileNotFoundError(f"No model found at {path}")

class DataAugmentation:
    """
    Component for applying data augmentation to image datasets.
    """
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def apply(self, image):
        """
        Apply data augmentation to an image.

        Args:
            image: Input image to augment.

        Returns:
            Augmented image tensor.
        """
        return self.transform(image)

# Model Evaluation Component
class ModelEvaluator:
    """
    Component for evaluating the performance of the defect detection model.
    """
    def __init__(self, model: DefectDetectionModel):
        self.model = model

    def evaluate(self, dataloader: DataLoader):
        """
        Evaluate the model on a given dataset.

        Args:
            dataloader (DataLoader): DataLoader containing the evaluation dataset.

        Returns:
            float: Accuracy of the model on the dataset.
        """
        self.model.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in dataloader:
                images, labels = images.to(self.model.device), labels.to(self.model.device)
                outputs = self.model.model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        accuracy = 100 * correct / total
        logger.info(f"Model accuracy: {accuracy:.2f}%")
        return accuracy

# Training Component
class ModelTrainer:
    """
    Component for training the defect detection model.
    """
    def __init__(self, model: DefectDetectionModel, criterion, optimizer):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer

    def train(self, dataloader: DataLoader, epochs: int):
        """
        Train the model on a given dataset.

        Args:
            dataloader (DataLoader): DataLoader containing the training dataset.
            epochs (int): Number of epochs to train the model.
        """
        self.model.model.train()
        for epoch in range(epochs):
            running_loss = 0.0
            for images, labels in dataloader:
                images, labels = images.to(self.model.device), labels.to(self.model.device)
                self.optimizer.zero_grad()
                outputs = self.model.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()
            logger.info(f"Epoch {epoch + 1}, Loss: {running_loss / len(dataloader):.4f}")
