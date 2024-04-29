from typing import List

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    Body,
)
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.repository.photos import get_photo_by_id, update_photo_description
from src.schemas import PhotoOut, UserOut
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User
from src.repository import photos as photos_repository


router = APIRouter(prefix="/photos", tags=["photos"])

# Moze taki przeniesiemy to do config.py
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


@router.patch("/{photo_id}/description")
async def edit_photo_description(
    photo_id: int,
    description: str = Form(""),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> PhotoOut:
    """
    Edit photo description

    Args:
        photo_id (int): Photo ID
        description (str): new description
        current_user (User): Current authenticated user
        db (Session): Database

    Returns:
        PhotoOut: Updated photo object
    """
    updated_photo = update_photo_description(photo_id, description, current_user, db)
    if not updated_photo:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update photo description",
        )
    return updated_photo
