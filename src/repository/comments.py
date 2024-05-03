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
    return CommentOut(
        id=new_comment.id,
        text=new_comment.text,
        user_id=new_comment.user_id,
        photo_id=new_comment.photo_id,
        date_posted=new_comment.date_posted,
        date_updated=new_comment.date_updated,
    )


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
    return CommentOut(
        id=comment.id,
        text=comment.text,
        user_id=comment.user_id,
        photo_id=comment.photo_id,
        date_posted=comment.date_posted,
        date_updated=comment.date_updated,
    )


async def delete_comment(comment_id: int, db: Session):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    db.delete(comment)
    db.commit()
    return CommentOut(
        id=comment.id,
        text=comment.text,
        user_id=comment.user_id,
        photo_id=comment.photo_id,
        date_posted=comment.date_posted,
        date_updated=comment.date_updated,
    )

async def get_comments_list(photo_id: int, db: Session):
    """
    Downloading the list of all comments associated with a specific photo.

    Parameters:
    - photo_id (int): The ID of the photo for which comments are to be downloaded.
    - db (Session): Database session dependency.

    Raises:
    - HTTPException:
        - 404 NOT FOUND - If the specified photo does not exist or if there are no comments associated with the photo.
        - 401 UNAUTHORIZED - If the user is not authenticated.

    Returns:
        dict: A dictionary containing the list of comments associated with the photo. Each comment is represented as a dictionary with keys 'comment id', 'comment text', and 'author'.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    comments = db.query(Comment).filter(Comment.photo_id == photo_id).all()
    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    comments_json = [{"comment id": comment.id, "comment text": comment.text, "author": comment.user_id} for comment in comments]
    return {"comments": comments_json}