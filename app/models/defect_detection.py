import torch
from torchvision import models, transforms
from torch.utils.data import DataLoader
import os

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
        print(f"Model saved to {path}")

    def load_model(self, path: str):
        """
        Load the model from a specified path.

        Args:
            path (str): Path to load the model from.
        """
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            print(f"Model loaded from {path}")
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
