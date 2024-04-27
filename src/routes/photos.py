from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from fastapi.responses import StreamingResponse
from src.database.db import get_db
from src.schemas import PhotoOut
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User
from src.repository import photos as photos_repository
import qrcode
from io import BytesIO


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

    tags = tags[0].split(",")

    unique_tags= list(set(tags))
    if len(unique_tags) >= 5:
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
@router.get("/qr/{file_path}")
async def generation_qr(file_path:str):
    qr= qrcode.make(file_path)
    buffer=BytesIO
    qr.save(buffer, format="PGN")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")