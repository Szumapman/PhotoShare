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

    if tag_name.strip():
        normalized_tag_name = tag_name.lower()
        tag = db.query(Tag).filter(Tag.tag_name == normalized_tag_name).first()
        if not tag:
            original_tag_name = tag_name
            tag = Tag(tag_name=normalized_tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
            tag.original_tag_name = original_tag_name
        return tag
    else:
        raise ValueError("Tag name cannot be empty or contain only whitespace.")
