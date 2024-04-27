from datetime import datetime
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
    date_posted = datetime.now()
    new_comment = Comment(
        user_id=user_id, photo_id=photo_id, text=text, created_at=date_posted
    )
    return new_comment
