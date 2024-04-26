from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.schemas import PhotoOut
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User
from src.repository import photos as photos_repository


router = APIRouter(prefix="/photos", tags=["photos"])

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
    upload_result = cloudinary.uploader.upload(file.file)
    photo_url = upload_result["url"]
    tags = tags[0].split(",")
    new_photo = await photos_repository.upload_photo(
        photo_url, current_user.id, description, tags, db
    )
    return new_photo
