from sqlalchemy.orm import Session

from src.database.models import Comment
from src.schemas import CommentOut


async def add_comment(
    user_id: int, photo_id: int, text: str, db: Session
) -> CommentOut:
    """
    Adds a new comment to the database.

    Args:
        user_id (int): The ID of the user who posted the comment.
        photo_id (int): The ID of the photo to which the comment is added.
        text (str): The text content of the comment.
        db (Session): A database session

    Returns:
        CommentOut: The newly created Comment object.

    """
    new_comment = Comment(
        text=text,
        photo_id=photo_id,
        user_id=user_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return CommentOut(
        id=new_comment.id,
        text=new_comment.text,
        date_posted=new_comment.date_posted,
        user_id=new_comment.user_id,
        photo_id=new_comment.photo_id,
    )
