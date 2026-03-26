from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from PIL import Image
import tempfile
import os
import uuid

from schemas import PredictionResponse
from database import get_session, MRIScan
from routers.auth import get_current_doctor
from model_loader import model_loader
from exceptions import ModelLoadError, InvalidImageError, FileSizeError
from config import settings

router = APIRouter(prefix="/predict", tags=["Prediction"])

# Magic bytes for image validation
IMAGE_MAGIC_BYTES = {
    b'\x89PNG\r\n\x1a\n': 'png',
    b'\xff\xd8\xff': 'jpeg',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
}

def validate_image_content(content: bytes) -> bool:
    return any(content.startswith(magic) for magic in IMAGE_MAGIC_BYTES)

@router.post("", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    doctor_id: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    # Check file size
    content = await file.read()
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "file_too_large",
                    "message": f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
                }
            }
        )
    
    # Validate magic bytes
    if not validate_image_content(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "invalid_image",
                    "message": "Invalid file type. Only PNG, JPEG images allowed"
                }
            }
        )
    
    # Check model loaded
    model = model_loader.get_model()
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "model_not_loaded",
                    "message": "ML model not loaded. Please try again later."
                }
            }
        )
    
    from tensorflow.keras.applications.efficientnet import preprocess_input
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        img = Image.open(tmp_path)
        if img.format not in ['PNG', 'JPEG']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "invalid_image",
                        "message": "Invalid image format"
                    }
                }
            )
        
        # Save uploaded file
        filename = f"{uuid.uuid4()}.png"
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        dest_path = os.path.join(uploads_dir, filename)
        
        img = img.convert("RGB")
        img.save(dest_path)
        
        # Preprocess and predict
        img = img.resize((224, 224))
        x = np.array(img, dtype=np.float32)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        
        preds = model.predict(x, verbose=0)[0]
        pred_index = int(np.argmax(preds))
        confidence_score = float(preds[pred_index] * 100)
        
        class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']
        raw_class = class_names[pred_index]
        
        tumor_detected = raw_class != "notumor"
        
        display_names = {
            "glioma": "Glioma",
            "meningioma": "Meningioma",
            "pituitary": "Pituitary Tumor",
            "notumor": "No Tumor"
        }
        
        tumor_type = display_names[raw_class]
        
        if tumor_detected:
            if confidence_score >= 85:
                analysis_notes = f"{tumor_type} detected with high confidence. Findings strongly suggest pathology. Clinical correlation advised."
            elif confidence_score >= 65:
                analysis_notes = f"{tumor_type} detected with moderate confidence. Further imaging or expert review recommended."
            else:
                analysis_notes = f"Possible {tumor_type.lower()} detected with low confidence. Manual radiologist review is required."
        else:
            analysis_notes = "No tumor detected. Brain MRI appears within normal limits. If symptoms persist, further evaluation is recommended."
        
        # Save scan to database
        scan = MRIScan(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            doctor_id=doctor_id,
            image_path=filename,
            analysis_status="completed",
            tumor_detected=tumor_detected,
            confidence_score=confidence_score,
            tumor_type=tumor_type if tumor_detected else None,
            tumor_location="Frontal Lobe" if tumor_detected else None,
            analysis_notes=analysis_notes
        )
        session.add(scan)
        await session.commit()
        
        return PredictionResponse(
            tumor_detected=tumor_detected,
            confidence_score=round(confidence_score, 2),
            tumor_type=tumor_type if tumor_detected else None,
            tumor_location="Frontal Lobe" if tumor_detected else None,
            analysis_notes=analysis_notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "analysis_failed",
                    "message": f"Analysis failed: {str(e)}"
                }
            }
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)