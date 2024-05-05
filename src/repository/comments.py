from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from src.database.models import Comment, Photo
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
    return CommentOut.from_orm(new_comment)


async def update_comment(
    comment_id: int, text: str, user_id: int, db: Session
) -> CommentOut:
    """
    Update an existing comment in the database.

    Args:
        comment_id (int): The ID of the comment to update.
        text (str): The updated text content of the comment.
        user_id (int): The ID of the user who posted the comment.
        db (Session): Database session.

    Returns:
        Comment: The updated Comment object.

    Raises:
        HTTPException: If the comment with the given ID does not exist.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can update the comment",
        )
    try:
        comment.text = text
        db.commit()
        db.refresh(comment)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Error updating comment: {}".format(str(e))
        )
    return CommentOut.from_orm(comment)


async def delete_comment(comment_id: int, db: Session):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    db.delete(comment)
    db.commit()
    return CommentOut.from_orm(comment)


async def get_comments(photo_id: int, db: Session) -> list[CommentOut]:
    """
    Downloading the list of all comments associated with a specific photo.

    Parameters:
    - photo_id (int): The ID of the photo for which comments are to be downloaded.
    - db (Session): Database session dependency.

    Returns:
        list[CommentOut]: The list of comments associated with a photo.

    Raises:
    - HTTPException:
        - 404 NOT FOUND - If the specified photo does not exist.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return [comments for comments in photo.comments if comments]
