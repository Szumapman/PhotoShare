from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import tags
from src.schemas import UserOut, TagIn, TagOut, PhotoIn
from src.services.auth import Auth

router = APIRouter(prefix="/tags", tags=["tags"])
auth_service = Auth()


@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def get_or_create_tag(
    tag_data: TagIn,
    photo_data: PhotoIn,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new tag or get an existing tag for a photo.

    Args:
        tag_data (TagIn): The tag data to create or get.
        photo_data (PhotoIn): The photo data associated with the tag.
        current_user (UserOut): The currently authenticated user.
        db (Session): The database session.

    Returns:
        TagOut: The created or retrieved tag.

    """

    tag = tags.get_or_create_tag(db, tag_data.tag_name)
    return tag
