from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.schemas import TagOut, UserOut
from src.database.models import Photo, Tag, PhotoTag


def _get_photo(photo_id: int, db: Session) -> Photo:
    """
    Helper function to retrieve a photo from the database

    Args:
        photo_id (int): The id of the photo to retrieve
        db (Session): SQLAlchemy session

    Return:
        Photo: The photo from the database

    Raises:
        HTTPException if the photo is not found
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


def _get_tag(tag_id: int, db: Session) -> Tag:
    """
    Helper function to retrieve a tag from the database.

    Args:
        tag_id (int): The id of the tag to retrieve
        db (Session): SQLAlchemy session

    Returns:
        Tag: The tag from the database

    Raises:
        HTTPException if the tag is not found
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


async def get_tags(photo_id: int, db: Session) -> list[TagOut]:
    """
    Function to retrieve a list of tags from the database.

    Args:
         photo_id (int): The id of the photo to retrieve
         db (Session): SQLAlchemy session

    Returns:
        list[TagOut]: The list of tags from the database
    """
    photo = _get_photo(photo_id, db)
    tags = [tags for tags in photo.tags if tags]
    return tags


async def add_tag(
    photo_id: int, tag_name: str, user_id: int, db: Session
) -> list[TagOut]:
    """
    Add a tag to the database and connect it with the photo.

    Args:
        photo_id (int): The id of the photo
        tag_name (str): The name of the tag
        user_id (int): The id of the user
        db (Session): SQLAlchemy session

    Returns:
        list[TagOut]: The list of tags from the database connected to the photo.

    Raises:
        HTTPException (403_FORBIDDEN) if action is not performef by the photo owner,
        HTTPException (400_BAD_REQUEST) if photo already has five tags or has this tag.
    """
    photo = _get_photo(photo_id, db)
    if photo.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the photo owner can add tags",
        )
    if len(photo.tags) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Photo tags can only have five tags, to add new tag you have to first delete another tag.",
        )
    tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
    if not tag:
        tag = Tag(tag_name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    photo_tag = (
        db.query(PhotoTag)
        .filter(PhotoTag.photo_id == photo_id, PhotoTag.tag_id == tag.id)
        .first()
    )
    if photo_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This photo already has this tag",
        )
    photo_tag = PhotoTag(photo_id=photo_id, tag_id=tag.id)
    db.add(photo_tag)
    db.commit()
    db.refresh(photo)
    return [tags for tags in photo.tags if tags]


async def update_tag(
    photo_id: int, tag_id: int, tag_update_name: str, current_user_id: int, db: Session
) -> list[TagOut]:
    """
    Function to update a tag in the database.

    Args:
        photo_id (int): The id of the photo
        tag_id (int): The id of the tag
        tag_update_name (str): The new name of the tag
        current_user_id (int): The id of the user
        db (Session): SQLAlchemy session

    Returns:
        list[TagOut]: The list of tags from the database connected to the photo.

    Raises:
        HTTPException (400_BAD_REQUEST) if photo already has this tag.
    """
    photo = _get_photo(photo_id, db)
    tag = _get_tag(tag_id, db)
    if photo.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the photo owner can update tags",
        )
    photo_tag_old = (
        db.query(PhotoTag)
        .filter(PhotoTag.tag_id == tag.id, PhotoTag.photo_id == photo_id)
        .first()
    )
    new_tag = db.query(Tag).filter(Tag.tag_name == tag_update_name).first()
    if not new_tag:
        new_tag = Tag(tag_name=tag_update_name)
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
    photo_tag = (
        db.query(PhotoTag)
        .filter(PhotoTag.photo_id == photo_id, PhotoTag.tag_id == new_tag.id)
        .first()
    )
    if photo_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This photo already has this tag",
        )
    photo_tag = PhotoTag(photo_id=photo_id, tag_id=new_tag.id)
    db.add(photo_tag)
    db.delete(photo_tag_old)
    db.commit()
    photo_tags = db.query(PhotoTag).filter(PhotoTag.tag_id == tag.id).all()
    if not photo_tags:
        db.delete(tag)
        db.commit()
    db.refresh(photo)
    return [tags for tags in photo.tags if tags]


async def delete_tag(
    photo_id: int, tag_id: int, user: UserOut, db: Session
) -> list[TagOut]:
    """
    Function to delete a tag from the database or it connection with the photo.

    Args:
        photo_id (int): The id of the photo
        tag_id (int): The id of the tag
        user (UserOut): The user whose performed the action
        db (Session): SQLAlchemy session

    Returns:
        list[TagOut]: The list of tags from the database connected to the photo.

    Raises:
        HTTPException (403_FORBIDDEN) if action is not performed by the photo owner, moderator or admin.
    """
    photo = _get_photo(photo_id, db)
    tag = _get_tag(tag_id, db)
    if photo.user_id != user.id or user.role in [
        "admin",
        "moderator",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the photo owner, moderator or admin can delete tags",
        )
    photo_tags = db.query(PhotoTag).filter(PhotoTag.tag_id == tag.id).all()
    if len(photo_tags) > 1:
        photo_tag = (
            db.query(PhotoTag)
            .filter(PhotoTag.photo_id == photo_id, PhotoTag.tag_id == tag_id)
            .first()
        )
        db.delete(photo_tag)
        db.commit()
    else:
        db.delete(tag)
        db.commit()
    db.refresh(photo)
    return [tags for tags in photo.tags if tags]
