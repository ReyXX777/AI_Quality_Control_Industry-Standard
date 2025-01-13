import torch
from torchvision import models

class DefectDetectionModel:
    def __init__(self):
        self.model = models.resnet18(pretrained=True)  # Pretrained ResNet
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 2)  # Binary classification

    def predict(self, image_tensor):
        self.model.eval()
        with torch.no_grad():
            output = self.model(image_tensor)
        return torch.argmax(output, dim=1).item()
