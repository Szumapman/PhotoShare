from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.schemas import TagOut, UserOut
from src.services.auth import auth_service
from src.repository import tags as tags_repository
from src.database.db import get_db
from src.conf.constant import MAX_TAG_NAME_LENGTH

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/{photo_id}", response_model=list[TagOut])
async def get_tags(
    photo_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all tags for a photo

    Args:
         photo_id (int): Photo ID
         current_user (UserOut): Current user
         db (Session): Database

    Returns:
        list[TagOut]: List of tags
    """
    tags = await tags_repository.get_tags(photo_id, db)
    return tags


@router.post("/{photo_id}", response_model=list[TagOut])
async def add_tag(
    photo_id: int,
    tag_name: str,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a tag to a photo.

    Args:
        photo_id (int): Photo ID
        tag_name (str): Tag name
        current_user (UserOut): Current user
        db (Session): Database

    Returns:
        list[TagOut]: List of tags connected to a photo

    Raises:
        HTTPException: If tag_name is too long.
    """
    if len(tag_name) > MAX_TAG_NAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag name must be less than {MAX_TAG_NAME_LENGTH} characters",
        )
    tags = await tags_repository.add_tag(photo_id, tag_name, current_user.id, db)
    return tags


@router.patch("/{photo_id}/{tag_id}", response_model=list[TagOut])
async def update_tag(
    photo_id: int,
    tag_id: int,
    tag_update_name: str,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a tag connected to a photo.

    Args:
        photo_id (int): Photo ID
        tag_id (int): Tag ID
        tag_update_name (str): Tag new name
        current_user (UserOut): Current user
        db (Session): Database

    Returns:
        list[TagOut]: List of tags connected to a photo

    Raises:
        HTTPException: If tag_update_name is too long.
    """
    if len(tag_update_name) > MAX_TAG_NAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag name must be less than {MAX_TAG_NAME_LENGTH} characters",
        )
    tags = await tags_repository.update_tag(
        photo_id, tag_id, tag_update_name, current_user.id, db
    )
    return tags


@router.delete("/{photo_id}/{tag_id}", response_model=list[TagOut])
async def delete_tag(
    photo_id: int,
    tag_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a tag connected to a photo.

    Args
        photo_id (int): Photo ID
        tag_id (int): Tag ID
        current_user (UserOut): Current user
        db (Session): Database

    Returns:
        list[TagOut]: List of tags connected to a photo
    """
    tags = await tags_repository.delete_tag(photo_id, tag_id, current_user, db)
    return tags
