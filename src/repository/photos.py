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

    for tag_name in set(tags):
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


async def get_photo_by_id(photo_id: int, db: Session) -> PhotoOut | None:
    """
    Get photo by id

    Args:
        photo_id (int): photo id
        db (Session): database session

    Returns:
        PhotoOut | None: photo object or None if not found Photo with provided id
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        return None
    return PhotoOut(
        id=photo.id,
        file_path=photo.file_path,
        description=photo.description,
        upload_date=photo.upload_date,
    )
