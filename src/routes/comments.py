from sqlalchemy.orm import Session
from src.database.models import Comment
from src.schemas import CommentIn, CommentOut, UserRoleValid, UserOut
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


@router.put("/comments/{comment_id}/", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    updated_at: CommentIn,
    current_user: str = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the content of a comment if the current user is the owner of the comment.

    Args:
        comment_id (int): The ID of the comment to update.
        updated_at (CommentIn): Updated data for the comment.
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

    comment.text = updated_at.text
    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}/")
async def delete_comment(
    comment_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes a comment if the current user is an admin/moderator.

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
