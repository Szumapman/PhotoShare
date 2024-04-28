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

async def delete_photo(
    photo_id: int, user: UserOut, db: Session
) -> PhotoOut | None:
    """
    Delete a photo from the database if it belongs to the specified user or if the user is administrator.

    Args:
        photo_id (int): The ID of the photo to be deleted.
        user (UserOut): An instance of UserOut representing the user performing the deletion.
        db (Session): The database session.

    Returns:
        PhotoOut | None: If the photo is successfully deleted, returns the deleted photo object.
            If the photo does not exist or does not belong to the specified user, or the user does not have access, returns None.
    """
    photo = db.query(Photo).filter(
        (Photo.id == photo_id) & 
        ((Photo.user_id == user.id) | (user.role == "admin"))
    ).first()

    if photo:
        db.delete(photo)
        db.commit()
    return photo