from fastapi import APIRouter, FastAPI, File, UploadFile, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
import shutil
import cloudinary
import cloudinary.uploader

from src.conf.config import settings
from src.database.db import get_db
from sqlalchemy.orm import Session
from src.database.models import Photo
from src.repository import photos as repository_photo
from src.services.auth import Auth

# import qrcode
from io import BytesIO

# app = FastAPI()
router = APIRouter(prefix="/photo", tags=["photo"])
cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
)

router = APIRouter(
    prefix="/photo", tags=["photo"]
)  # Tutaj określamy tagi dla tego routera


@router.get("/get_photo", tags=["photo"])  # Tutaj określamy tagi dla tej ścieżki API
async def get_photo_file_path(file_path: str, db: Session = Depends(get_db)):
    return db.query(Photo).filter(Photo.file_path == file_path)


@router.post("/upload", tags=["photo"])
async def upload(file: UploadFile, db: Session = Depends(get_db)):
    result = cloudinary.uploader.upload(file.file)
    image_url = result["url"]
    new_photo = Photo(file_path=image_url, description="")
    try:
        db.add(new_photo)
        db.commit()
    except Exception as e:
        print("Error while saving photo to database:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while saving photo to database",
        )

    return {"message": "Photo successfully added", "image_url": image_url}
