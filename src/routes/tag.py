from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Photo
from src.repository import tags
from src.services.auth import Auth

router = APIRouter(prefix="/tags", tags=["tags"])
auth_service = Auth()


@router.post("/photos/{photo_id}/tags/", response_model=None)
def add_tag_to_photo(
    photo_id: int,
    tag1: Optional[str] = Form(None),
    tag2: Optional[str] = Form(None),
    tag3: Optional[str] = Form(None),
    tag4: Optional[str] = Form(None),
    tag5: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Add tags to a photo in the database.

    Args:
        photo_id (int): The ID of the photo to add tags to.
        tag1 (Optional[str]): The first tag to add to the photo.
        tag2 (Optional[str]): The second tag to add to the photo.
        tag3 (Optional[str]): The third tag to add to the photo.
        tag4 (Optional[str]): The fourth tag to add to the photo.
        tag5 (Optional[str]): The fifth tag to add to the photo.
        db (Session, optional): The database session.

    Raises:
        HTTPException: If the maximum number of tags has been reached for this photo.
        HTTPException: If a tag already exists for this photo.

    Returns:
        None
    """

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        tags_list = [tag1, tag2, tag3, tag4, tag5]
        for tag_name in tags_list:
            if tag_name is not None:
                if len(photo.tags) >= 5:
                    raise HTTPException(
                        status_code=400,
                        detail="Maximum number of tags reached for this photo",
                    )
                if any(
                    existing_tag.tag_name == tag_name for existing_tag in photo.tags
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Tag '{tag_name}' already exists for this photo",
                    )
                tag = tags.get_or_create_tag(db, tag_name)
                photo.tags.append(tag)
        db.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"Photo not found with ID: {photo_id}"
        )
