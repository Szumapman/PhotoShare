from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Photo, Tag, PhotoTag
from src.schemas import PhotoOut, UserOut


async def upload_photo(
    file_path: str,
    qr_code_url: str,
    user_id: int,
    description: str,
    tags: List[str],
    db: Session,
) -> PhotoOut:
    """
    Upload new photo to database

    Args:
         file_path (str): photo url
         qr_code_url (str): qrcode url
         user_id (int): user id
         description (str): description
         tags (List[str]): tags
         db (Session): database session

    Returns:
        PhotoOut: PhotoOut object
    """
    new_photo = Photo(
        file_path=file_path,
        qr_path=qr_code_url,
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
        qr_path=new_photo.qr_path,
        transformation=new_photo.transformation,
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
    return photo


async def delete_photo(photo_id: int, user: UserOut, db: Session) -> PhotoOut | None:
    """
    Delete a photo from the database if it belongs to the specified user or if the user is administrator.

    Args:
        photo_id (int): The ID of the photo to be deleted.
        user (UserOut): An instance of UserOut representing the user performing the deletion.
        db (Session): The database session.

    Returns:
        PhotoOut: Returns the deleted photo object.

    Raises:
        HTTPException: 404 If the photo does not exist.
        HTTPException: 403 If the user is not administrator or the photo owner.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    if photo.user_id == user.id or user.role == "admin":
        db.delete(photo)
        db.commit()
        return photo
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only owner of the photo or admin can delete it.",
    )
