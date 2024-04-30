import re
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, EmailStr, field_validator


class UserRoleValid(str, Enum):
    admin = "admin"
    moderator = "moderator"
    standard = "standard"


class UserIn(BaseModel):
    """
    Data model for creating new users.

    Attributes:
        username (str): The username of the user. Must be between 4 and 16 characters.
        email (str): The email address of the user.
        password (str): The password of the user. Must be between 6 and 30 characters.

    """

    username: str = Field(min_length=4, max_length=16)
    email: EmailStr = Field(max_length=150, unique=True)
    password: str = Field(min_length=6, max_length=30)

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        elif len(password) > 30:
            raise ValueError("Password must be at most 30 characters long")
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{6,30}$", password):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit and one special character"
            )
        return password


class UserOut(UserIn):
    """
    Data model for retrieving users.
    The `UserOut` model inherits from the `UserIn` model, overwrite password field, and it's validator
    and adds additional fields: `id`, 'role', and 'avatar'

    Attributes:
        id (int): The unique identifier of the user.
        password (str): Hashed password.
        role (UserRoleValid): The role of the user.
        avatar (str): The avatar URL of the user.
        is_active(bool): Whether the user is active or baned.
    """

    id: int
    password: str = Field(max_length=255)
    role: UserRoleValid
    avatar: str = "default_avatar.jpg"
    is_active: bool = True

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        if len(password) > 255:
            raise ValueError("Password hash is too long, check hash method.")
        return password

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    """
    Data model for tokens.

    Attributes:
        access_token (str): The access token.
        refresh_token (str): The refresh token.
        token_type (str): The type of token.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Data model for requesting email confirmation.

    Attributes:
        email (EmailStr): The email address for which confirmation is requested.

    """

    email: EmailStr


class UserRole(BaseModel):
    """
    Data model for changing user roles.

    Attributes:
        role (str): The role of the user.
    """

    role: UserRoleValid


class PhotoOut(BaseModel):
    id: int
    file_path: str
    description: str
    upload_date: datetime


class CommentOut(BaseModel):
    id: int
    text: str
    photo_id: int
    user_id: int
    date_posted: datetime
    date_updated: datetime | None
