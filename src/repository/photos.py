from typing import List

from sqlalchemy.orm import Session

from src.database.models import Photo, Tag, PhotoTag
from src.schemas import PhotoOut, UserOut


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


async def get_photo(photo_id: int, db: Session) -> str | None:
    """
    Retrieve the file path associated with a photo from the database if it belongs to the specified user or if the user is administrator.

    Args:
        photo_id (int): The ID of the photo to be retrieved.
        user (UserOut): An instance of UserOut representing the user requesting the photo.
        db (Session): The database session.

    Returns:
        str | None: The file path associated with the photo. Returns None if the photo with provided id is not found.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    return photo.file_path if photo else None
