from typing import List

from sqlalchemy.orm import Session

from src.database.models import Photo, Tag, PhotoTag
from src.schemas import PhotoOut


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
        print(tag_name)
        tag_name = tag_name.strip()
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
