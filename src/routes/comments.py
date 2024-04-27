from sqlalchemy.orm import Session
from src.database.models import Comment
from src.schemas import CommentIn, CommentOut
from fastapi import APIRouter, HTTPException, Depends

from src.services.auth import Auth
from src.database.db import get_db


router = APIRouter(prefix="/comments", tags=["comments"])
auth_service = Auth()


@router.post("/photos/{photo_id}/comments/", response_model=CommentOut)
async def create_comment(
    comment_data: CommentIn,
    current_user: str = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new comment associated with a photo.

    Args:
        comment_data (CommentIn): Data for the new comment.
        current_user (str, optional): Current user's authentication token.
        db (Session, optional): Database session.

    Returns:
        CommentOut: The newly created comment.

    Raises:
        HTTPException: If the user is not authorized.
    """

    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_comment = Comment(
        photo_id=comment_data.photo_id, user_id=current_user.id, text=comment_data.text
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment
