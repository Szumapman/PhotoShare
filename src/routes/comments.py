from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session
from src.schemas import CommentOut
from fastapi import APIRouter, Depends, HTTPException, status

from src.services.auth import Auth
from src.database.db import get_db
from src.schemas import UserOut, UserRoleValid
from src.repository.comments import add_comment
from src.database.models import Comment

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


@router.put("/comments/{comment_id}/", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    text: str,
    current_user: str = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the content of a comment if the current user is the owner of the comment.

    Route: PUT /comments/{comment_id}/

    Args:
        comment_id (int): The ID of the comment to update.
        text (str): Updated data for the comment.
        current_user (str): Current user's authentication token.
        db (Session): Database session.

    Returns:
        CommentOut: The updated comment.

    Raises:
        HTTPException: If the comment does not exist or if the current user is not the owner of the comment.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Forbidden: You can only edit your own comments"
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="Comment text cannot be empty")

    try:
        comment.text = text
        db.commit()
        db.refresh(comment)
        return comment
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error updating comment: {}".format(str(e))
        )


@router.delete("/comments/{comment_id}/")
async def delete_comment(
    comment_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes a comment if the current user is an admin/moderator.

    Route: DELETE /comments/{comment_id}/

    Args:
        comment_id (int): The ID of the comment to delete.
        current_user (str): Current user's authentication token.
        db (Session): Database session.

    Returns:
        dict: Confirmation message on successful deletion.

    Raises:
        HTTPException: If the comment does not exist, or if the current user is not authorized to delete the comment.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.role in [UserRoleValid.admin, UserRoleValid.moderator]:
        db.delete(comment)
        db.commit()
        return {"message": "Comment deleted successfully"}
    else:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Standard users are not authorized to delete comments",
        )
