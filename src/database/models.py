from sqlalchemy import Column, Integer, String, ForeignKey, Date, func, create_engine
from sqlalchemy.sql.sqltypes import DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class User(Base):
    """
        Defines a user of the system, capable of uploading photos and posting comments.
        Includes user identification, authentication, and contact details.

        :param user_id: Primary key.
        :type user_id: int
        :param name_to_show: Required, up to 50 characters, must be unique and is used for display purposes.
        :type name_to_show: str
        :param first_name: Required, user's first name, up to 50 characters.
        :type first_name: str
        :param last_name: Required, user's last name, up to 50 characters.
        :type last_name: str
        :param birth_date: Required, user's date of birth.
        :type birth_date: Date
        :param email: Required, up to 50 characters, must be unique.
        :type email: str
        :param phone_number: Optional, user's phone number, up to 15 characters.
        :type phone_number: str
        """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, unique=True)
    name_to_show = Column(String(50), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)
    email = Column(String, nullable=False, unique=True)
    verified = Column(Boolean, default=False, nullable=False)
    phone_number = Column(String(15))

    photos = relationship('Photo', back_populates='user')
    comments = relationship('Comment', back_populates='user')


class Photo(Base):
    """
        Represents a photo uploaded by a user.
        Contains file paths and metadata about the upload.

        :param photo_id: Primary key.
        :type photo_id: int
        :param file_path: Required, the path to the photo file.
        :type file_path: str
        :param upload_date: Automatically set to the current time upon upload.
        :type upload_date: DateTime
        :param user_id: Foreign key to the user who uploaded the photo.
        :type user_id: int
        """
    __tablename__ = 'photos'
    photo_id = Column(Integer, primary_key=True)
    file_path = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.user_id'))

    user = relationship('User', back_populates='photos')
    comments = relationship('Comment', back_populates='photo')
    tags = relationship('Tag', secondary='photo_tags', back_populates='photos')


class Comment(Base):
    """
        Represents a comment made by a user on a photo.
        Contains the comment text and metadata.

        :param comment_id: Primary key.
        :type comment_id: int
        :param text: Required, the content of the comment.
        :type text: str
        :param date_posted: Automatically set to the current time when the comment is posted.
        :type date_posted: DateTime
        :param photo_id: Foreign key to the commented photo.
        :type photo_id: int
        :param user_id: Foreign key to the user who made the comment.
        :type user_id: int
        """
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    date_posted = Column(DateTime, default=func.now())

    photo_id = Column(Integer, ForeignKey('photos.photo_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))

    user = relationship('User', back_populates='comments')
    photo = relationship('Photo', back_populates='comments')


class Tag(Base):
    """
        Represents a tag that can be associated with multiple photos.
        Contains the name of the tag.

        :param tag_id: Primary key.
        :type tag_id: int
        :param tag_name: Required, the name of the tag.
        :type tag_name: str
        """
    __tablename__ = 'tags'
    tag_id = Column(Integer, primary_key=True)
    tag_name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    photos = relationship('Photo', secondary='photo_tags', back_populates='tags')


class PhotoTag(Base):
    """
        Represents a junction table for many-to-many relationship between photos and tags.
        Allows tagging photos with multiple tags.

        :param photo_id: Foreign key to the photo, part of the primary key.
        :type photo_id: int
        :param tag_id: Foreign key to the tag, part of the primary key.
        :type tag_id: int
        """
    __tablename__ = 'photo_tags'
    photo_id = Column(Integer, ForeignKey('photos.photo_id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.tag_id'), primary_key=True)
