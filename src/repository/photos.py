from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

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


def update_photo_description(
    photo_id: int, new_description: str, current_user: UserOut, db: Session
):
    """
    Update photo description

    Args:
        photo_id (int): photo id
        new_description (str): new photo description
        current_user (UserOut): current authenticated user
        db (Session): database session

    Returns:
        PhotoOut: updated photo object
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    if photo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this photo",
        )
    photo.description = new_description
    db.commit()
    db.refresh(photo)
    return PhotoOut(
        id=photo.id,
        file_path=photo.file_path,
        description=photo.description,
        upload_date=photo.upload_date,
    )
