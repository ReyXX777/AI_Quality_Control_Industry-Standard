from PIL import Image
from torchvision import transforms
import io

def preprocess_image(image_data: bytes):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    return transform(image).unsqueeze(0)  # Add batch dimension
