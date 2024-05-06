from typing import List, Optional, Type

from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Photo, Tag, PhotoTag, User, Rating
from src.schemas import PhotoOut, UserOut, PhotoSearchOut, RatingIn, RatingOut
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
    return PhotoOut.model_validate(new_photo)


async def get_photo_by_id(photo_id: int, db: Session) -> PhotoOut:
    """
    Get photo by id

    Args:
        photo_id (int): photo id
        db (Session): database session

    Returns:
        PhotoOut: photo object with provided id

    Raises:
        HTTPException: 404 Not Found if photo does not exist
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    photo_out = PhotoOut.model_validate(photo)
    return photo_out


def update_photo_description(
    photo_id: int, new_description: str, current_user: UserOut, db: Session
) -> PhotoOut:
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
    return PhotoOut.model_validate(photo)


async def delete_photo(photo_id: int, user: UserOut, db: Session) -> PhotoOut:
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
        return PhotoOut.model_validate(photo)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only owner of the photo or admin can delete it.",
    )


async def add_transformation(
    photo: Photo, transform_photo_url: str, params: list, db: Session
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
    return PhotoOut.model_validate(photo)


async def get_user_photos(user_id: int, db: Session) -> list[PhotoSearchOut]:
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
    return [PhotoSearchOut.model_validate(photo) for photo in photos if photos]


async def get_photos(db: Session) -> list[PhotoSearchOut]:
    """
    Get the list of all photos.

    Args:
         db (Session): Database session dependency.

    Returns:
        list[PhotoOut]: List of photos.
    """
    photos = db.query(Photo).all()
    return [PhotoSearchOut.model_validate(photo) for photo in photos if photos]


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
    photos = []
    if field == "upload_date":
        query_base = query_base.order_by(
            Photo.upload_date.desc() if sort == "desc" else Photo.upload_date.asc()
        )
        photos = query_base.all()
    elif field == "rating":
        photos = query_base.all()
        photos.sort(key=lambda photo: photo.average_rating, reverse=(sort == "desc"))
    return [PhotoSearchOut.model_validate(photo) for photo in photos if photos]


async def rate_photo(
    photo_id: int, rating_in: RatingIn, user_id: int, db: Session
) -> RatingOut:
    """
    Set user rating for a photo.

    Args:
        photo_id (int): id of photo to rate.
        rating_in (RatingIn): Rating to be set.
        user_id (int): User who rated photo.
        db (Session): Database session.

    Returns:
        RatingOut: Rating out of the photo.

    Raises:
         HTTPException: 404 NOT FOUND - If the photo does not exist.
         HTTPException: 403 FORBIDDEN - If the photo is rated by its owner.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )
    if photo.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot rate your own photo",
        )
    rating = db.query(Rating).filter_by(photo_id=photo_id, user_id=user_id).first()
    if rating:
        rating.score = rating_in.score
    else:
        rating = Rating(photo_id=photo_id, user_id=user_id, score=rating_in.score)
        db.add(rating)
    db.commit()
    db.refresh(rating)
    return RatingOut.model_validate(rating)
