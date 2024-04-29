from sqlalchemy.orm import Session
from src.schemas import CommentOut
from fastapi import APIRouter, Depends, HTTPException, status

from src.services.auth import Auth
from src.database.db import get_db
from src.schemas import UserOut
from src.repository.comments import add_comment


router = APIRouter(prefix="/comments", tags=["comments"])
auth_service = Auth()


@router.post("/{photo_id}", response_model=CommentOut)
async def create_comment(
    photo_id: int,
    comment: str,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new comment associated with a photo.

    Args:
        photo_id (int): The photo ID to comment on.
        comment (str): The new comment.
        current_user (UserOut): Current authenticated user.
        db (Session): Database session.

    Returns:
        CommentOut: The newly created comment.

    Raises:
        HTTPException: If the comment is consist of only whitespace.
    """
    if not comment.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment cannot be empty.",
        )
    new_comment = await add_comment(
        current_user.id,
        photo_id,
        comment,
        db,
    )
    return new_comment
