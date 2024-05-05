from sqlalchemy import Column, Integer, String, func, Boolean, Enum, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship, declarative_base
from src.conf.constant import (
    MAX_USERNAME_LENGTH,
    MAX_COMMENT_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_TAG_NAME_LENGTH,
)

Base = declarative_base()


class User(Base):
    """
    SQLAlchemy model representing a table of users.

    Attributes:
        id (int): The unique identifier for each user.
        username (str): The username of the user.
        email (str): The email address of the user (nullable).
        confirmed (bool): Flag indicating whether the user's email address is confirmed.
        role (str): Role of the user in the system, can take values of 'admin', 'moderator', or 'standard'.
        password (str): The password of the user. Note: It's recommended to store passwords hashed for security reasons.
        created_at (datetime): The timestamp indicating when the user account was created.
        avatar (str, optional): The URL or path to the user's avatar image (nullable).
        refresh_token (str, optional): The refresh token associated with the user (nullable).
        is_active (bool): Flag indicating whether the user is active or baned.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(MAX_USERNAME_LENGTH), nullable=False, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    role = Column(
        Enum("admin", "moderator", "standard", name="user_roles"), nullable=False
    )
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    photos = relationship("Photo", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    rights = relationship("Right", back_populates="user")


class Photo(Base):
    """
    Represents a photo uploaded by a user.
    Contains file paths and metadata about the upload.
    :param id: Primary key.
    :type id: int
    :param file_path: Required, the path to the photo file.
    :type file_path: str
    :param description: The description of the photo.
    :type description: str
    :param upload_date: Automatically set to the current time upon upload.
    :type upload_date: DateTime
    :param user_id: Foreign key to the user who uploaded the photo.
    :type user_id: int
    """

    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    file_path = Column(String(255), nullable=False)
    qr_path = Column(String(255), nullable=False)
    transformation = Column(JSON, nullable=True)
    description = Column(String(MAX_DESCRIPTION_LENGTH), nullable=False)
    upload_date = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="photos")
    comments = relationship("Comment", back_populates="photo")
    tags = relationship("Tag", secondary="photo_tags", back_populates="photos")
    ratings = relationship("Rating", back_populates="photo")


class Comment(Base):
    """
    Represents a comment made by a user on a photo.
    Contains the comment text and metadata.
    :param id: Primary key.
    :type id: int
    :param text: Required, the content of the comment.
    :type text: str
    :param date_posted: Automatically set to the current time when the comment is posted.
    :type date_posted: DateTime
    :param photo_id: Foreign key to the commented photo.
    :type photo_id: int
    :param user_id: Foreign key to the user who made the comment.
    :type user_id: int
    """

    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(String(MAX_COMMENT_LENGTH), nullable=False)
    date_posted = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now())

    photo_id = Column(Integer, ForeignKey("photos.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="comments")
    photo = relationship("Photo", back_populates="comments")


class Tag(Base):
    """
    Represents a tag that can be associated with multiple photos.
    Contains the name of the tag.
    :param id: Primary key.
    :type id: int
    :param tag_name: Required, the name of the tag.
    :type tag_name: str
    """

    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    tag_name = Column(String(MAX_TAG_NAME_LENGTH), nullable=False, unique=True)

    photos = relationship("Photo", secondary="photo_tags", back_populates="tags")


class PhotoTag(Base):
    """
    Represents a junction table for many-to-many relationship between photos and tags.
    Allows tagging photos with multiple tags.
    :param photo_id: Foreign key to the photo, part of the primary key.
    :type photo_id: int
    :param tag_id: Foreign key to the tag, part of the primary key.
    :type tag_id: int
    """

    __tablename__ = "photo_tags"
    photo_id = Column(Integer, ForeignKey("photos.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)

    photo = relationship("Photo", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

    __table_args__ = (UniqueConstraint("photo_id", "user_id", name="photo_user_uc"),)
