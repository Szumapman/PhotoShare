from typing import List
from sqlalchemy import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.database.db import get_db
from src.database.models import Photo, Tag, PhotoTag
from src.schemas import PhotoOut, Tag


async def upload_photo(
    file_path: str, user_id: int, description: str, tags: List[str], db: Session
):
    new_photo = Photo(
        file_path=file_path,
        description=description,
        user_id=user_id,
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)

    for tag_name in tags:
        tag_name = tag_name.strip().lower()
        if tag_name:
            tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
            if not tag:
                tag = Tag(tag_name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            photo_tag = PhotoTag(photo_id=new_photo.id, tag_id=tag.id)
            db.add(photo_tag)
    db.commit()

    return PhotoOut(
        id=new_photo.id,
        file_path=new_photo.file_path,
        description=new_photo.description,
        upload_date=new_photo.upload_date,
    )
async def new_upload_photo(
    file_path: str, user_id: int, db: Session
):
    new_phot = Photo(
        file_path=file_path,

        user_id=user_id,
    )
    db.add(new_phot)
    db.commit()
    db.refresh(new_phot)
    return new_phot
async def edit_tag(user_id: int, tag_id:int, new_tag_name:str, db:Session)-> Tag:
    tag=db.query(Tag).filter(Tag.id==tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not egsist")
    if tag.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access")
    tag.tag_name=new_tag_name

    db.commit()
    db.refresh(tag)
    return tag




    return tag