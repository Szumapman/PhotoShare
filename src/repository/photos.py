from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Photo, Tag, PhotoTag, User
from src.schemas import PhotoOut, UserOut, PhotoSearchOut
from src.conf.constant import PHOTO_SEARCH_ENUMS


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
    db.refresh(new_photo)
    return PhotoOut(
        id=new_photo.id,
        file_path=new_photo.file_path,
        qr_path=new_photo.qr_path,
        transformation=new_photo.transformation,
        description=new_photo.description,
        tags=new_photo.tags,
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
    return photo


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


async def add_transformation(
    photo: PhotoOut, transform_photo_url: str, params: list, db: Session
) -> PhotoOut:
    """
    Add a new transformation to the photo.

    Args:
         photo (PhotoOut): Photo object to be transformed.
         transform_photo_url (str): The url of the transformation.
         params (list): List of parameters to be passed to the transformation.
         db (Session): database session

    Returns:
        PhotoOut: Photo object with transformed photo.
    """
    transformations = photo.transformation or {}
    transformations[transform_photo_url] = params
    photo.transformation = None
    db.commit()
    photo.transformation = transformations
    db.commit()
    db.refresh(photo)
    return photo


async def get_user_photos(user_id: int, db: Session) -> list[PhotoOut]:
    """
    Get the list of all photos uploaded by a specific user.

    Args:
        user_id (int): The ID of the user whose photos are to be downloaded.
        db (Session): Database session dependency.

    Returns:
        list[PhotoOut]: List of photos uploaded by a specific user.

    Raises:
        HTTPException: 404 NOT FOUND - If the specified user does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    photos = db.query(Photo).filter(Photo.user_id == user_id).all()
    return photos


async def get_photos(db: Session) -> list[PhotoSearchOut]:
    """
    Get the list of all photos.

    Args:
         db (Session): Database session dependency.

    Returns:
        list[PhotoOut]: List of photos.
    """
    photos = db.query(Photo).all()
    return [PhotoSearchOut.from_orm(photo) for photo in photos if photos]


async def search_photos(
    query: Optional[str], sort_by: str, db: Session
) -> List[PhotoSearchOut]:
    """
    Search and sort photos based on the query and sort criteria.

    Args:
        query (str | None): Keywords to search in photo descriptions or tags.
        sort_by (str): Sorting criterion, either 'date' or 'rating' with -desc or -asc info.
        db (Session): Database session.

    Returns:
        List[PhotoSearchOut]: List of photos matching the search criteria.

    Raises:
        HTTPException: 502 Bad Gateway if invalid sort option is provided.
    """
    if sort_by not in PHOTO_SEARCH_ENUMS:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid sort option: {sort_by}",
        )
    query_base = db.query(Photo).filter(
        or_(
            Photo.description.ilike(f"%{query}%"),
            Photo.tags.any(Tag.tag_name.ilike(f"%{query}%")),
        )
    )
    field, sort = sort_by.split("-")
    if field == "upload_date":
        query_base = query_base.order_by(
            Photo.upload_date.desc() if sort == "desc" else Photo.upload_date.asc()
        )
    # add when rating ready
    # elif field == "rating":
    #     query_base = query_base.order_by(Photo.rating.desc() if sort == "desc" else Photo.reating.asc())

    photos = query_base.all()

    return [PhotoSearchOut.from_orm(photo) for photo in photos if photos]
