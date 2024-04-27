from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.repository.photos import get_photo_by_id
from src.schemas import PhotoOut
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User, Photo
from src.repository import photos as photos_repository


router = APIRouter(prefix="/photos", tags=["photos"])

# moze ten pszeniesc do config.py?
cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


@router.post("/", response_model=PhotoOut)
async def upload_photo(
    file: UploadFile = File(),
    description: str = Form(""),
    tags: list[str] = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> PhotoOut:
    tags = tags[0].split(",")
    if len(tags) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many tags provided. You can use max of 5 tags.",
        )
    upload_result = cloudinary.uploader.upload(file.file)
    photo_url = upload_result["url"]
    new_photo = await photos_repository.upload_photo(
        photo_url, current_user.id, description, tags, db
    )
    return new_photo


# Ciągniemy zdjęcie po linku.
@router.get("/{photo_id}/download")
async def download_photo(
        photo_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    photo = get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    return {"photo_url": photo.file_path}
