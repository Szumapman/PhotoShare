from sqlalchemy.orm import Session
from src.schemas import CommentOut
from fastapi import APIRouter, Depends, HTTPException, status

from src.services.auth import Auth
from src.database.db import get_db
from src.schemas import UserOut, UserRoleValid
from src.repository import comments as comment_repository
from src.repository import photos as photo_repository
from src.conf.constant import MAX_COMMENT_LENGTH

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
        HTTPException: If the comment is consist of only whitespace or comment is too long.
    """
    comment = comment.strip()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment cannot be empty.",
        )
    if len(comment) > MAX_COMMENT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comment cannot be longer than {MAX_COMMENT_LENGTH} characters.",
        )
    photo = photo_repository.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo does not exist.",
        )
    new_comment = await comment_repository.add_comment(
        current_user.id,
        photo_id,
        comment,
        db,
    )
    return new_comment


@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    comment_text: str,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the content of a comment if the current user is the owner of the comment.

    Args:
        comment_id (int): The ID of the comment to update.
        comment_text (str): Updated data for the comment.
        current_user (UserOut): Current user's authentication token.
        db (Session): Database session.

    Returns:
        CommentOut: The updated comment.
    """
    if not comment_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment cannot be empty.",
        )
    comment = await comment_repository.update_comment(
        comment_id, comment_text, current_user.id, db
    )
    return comment


@router.delete("/{comment_id}", response_model=CommentOut)
async def delete_comment(
    comment_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes a comment if the current user is an admin or moderator.

    Args:
        comment_id (int): The ID of the comment to delete.
        current_user (UserOut): Current user's authentication token.
        db (Session): Database session.

    Returns:
        CommentOut: the deleted comment.

    Raises:
        HTTPException: If the current user is not authorized to delete the comment.
    """

    if current_user.role in [UserRoleValid.admin, UserRoleValid.moderator]:
        comment = await comment_repository.delete_comment(comment_id, db)
        return comment
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Standard users are not authorized to delete comments",
        )
