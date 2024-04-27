from typing import List
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from fastapi.responses import StreamingResponse
from src.database.db import get_db
from src.schemas import PhotoOut
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User,Photo
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

@router.post("/", response_model=PhotoOut)
def manipulation_photo(photo_id:str,
                       width: Optional[int]= Query(None, deprecated="Szerokość"),
                       height:Optional[int]=Query(None,deprecated="Wysokość"),
                       crop:Optional[str]=Query(None,deprecated="Przycięcie wpisz: mfit,limit,pad,thumb,scale,fit,fill"),
                       effect:Optional[str]=Query(None,deprecated="Dodaj effekt: sepia,grayscale,vignette,blur,red,invert,"
                                                                  "brightness,saturation,pixelate"),
                       db:Session=Depends(get_db)):
    parms={}
    if width:
        parms["width"]=width
    if height:
        parms[height]=height
    if crop:
        parms["crop"]=crop
    if effect:
        parms["effect"]=effect
    if parms:
        manipul_photo= cloudinary.utils.cloudinary_url(photo_id, **parms)[0]
        new_photo=Photo(file_path=manipul_photo)
        db.add(manipul_photo)
        db.commit()
        db.refresh(manipul_photo)
    else:
        manipul_photo=photo_id
    return manipul_photo

