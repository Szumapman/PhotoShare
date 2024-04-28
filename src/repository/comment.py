from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.database.models import Comment


async def add_comment(user_id: int, photo_id: int, text: str) -> Comment:
    """
    Adds a new comment to the database.

    Args:
        user_id (int): The ID of the user who posted the comment.
        photo_id (int): The ID of the photo to which the comment is added.
        text (str): The text content of the comment.

    Returns:
        Comment: The newly created Comment object.

    """
    new_comment = Comment(
        user_id=user_id, photo_id=photo_id, text=text, created_at=datetime.now()
    )
    return new_comment


async def update_comment(comment_id: int, text: str, db: Session) -> Comment:
    """
    Update an existing comment in the database.

    Args:
        comment_id (int): The ID of the comment to update.
        text (str): The updated text content of the comment.
        db (Session): Database session.

    Returns:
        Comment: The updated Comment object.

    Raises:
        HTTPException: If the comment with the given ID does not exist.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.text = text
    db.commit()
    db.refresh(comment)
    return comment
