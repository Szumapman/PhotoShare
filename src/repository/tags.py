from sqlalchemy.orm import Session
from src.database.models import Tag


def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    """
    Get an existing tag from the database or create a new one if it doesn't exist.

    Args:
        db (Session): The database session.
        tag_name (str): The name of the tag.

    Returns:
        Tag: The tag retrieved from the database or newly created.
    """

    tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
    if not tag:
        tag = Tag(tag_name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag
