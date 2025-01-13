from fastapi import APIRouter, UploadFile
from models.defect_detection import DefectDetectionModel
from services.data_service import preprocess_image

router = APIRouter()
model = DefectDetectionModel()

@router.post("/detect")
async def detect_defect(file: UploadFile):
    image_tensor = preprocess_image(await file.read())
    prediction = model.predict(image_tensor)
    return {"defect_detected": bool(prediction)}
