from sqlalchemy import Column, Integer, String, func, Boolean, Enum
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base


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
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True,  autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    role = Column(Enum('admin', 'moderator', 'standard', name='user_roles'), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)