import re
from datetime import datetime
from enum import Enum
from typing import List, Dict

from pydantic import BaseModel, Field, EmailStr, field_validator

from src.conf.constant import (
    MAX_TAG_NAME_LENGTH,
    MAX_USERNAME_LENGTH,
)


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

    username: str = Field(min_length=4, max_length=MAX_USERNAME_LENGTH)
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


class UserOut(BaseModel):
    """
    Data model for retrieving users.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user. Must be between 4 and 16 characters.
        email (str): The email address of the user.
        role (UserRoleValid): The role of the user.
        avatar (str): The avatar URL of the user.
        is_active(bool): Whether the user is active or baned.
    """

    id: int
    username: str
    email: EmailStr
    role: UserRoleValid
    avatar: str = "default_avatar.jpg"
    is_active: bool = True

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


class CommentOut(BaseModel):
    id: int
    text: str
    photo_id: int
    user_id: int
    date_posted: datetime
    date_updated: datetime | None

    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """
    Data model for user public profile.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        avatar (str): The avatar URL of the user.
        photo_count (int): The number of photos uploaded by the user.
    """

    id: int
    username: str
    avatar: str
    photo_count: int

    class Config:
        from_attributes = True


class TransformationParameters(BaseModel):
    """
    Data model for transformation parameters.

    Attributes:
        background (str): The background color of the transformation (e.g. blue, red).
        aspect_ratio (str): The aspect ratio of the transformation (e.g. 16:10)
        gravity (str): The gravity of the transformation (e.g. south, west).
        angle (int): The angle of the transformation (e.g. -30 or 20).
        width (int): The width of the transformed image.
        height (int): The height of the transformed image.
        crop (str): The crop effects like:
            fill, lfill, fill_pad, crop, thumb, auto, scale, fit, limit, mfit, pad, lpad, mpad, imagga_scale, imagga_crop
        effects (list[str]): The cloudinary transformation effects like:
            art:al_dente/athena/audrey/aurora/daguerre/eucalyptus/fes/frost/hairspray/hokusai/incognito/linen/peacock
                /primavera/quartz/red_rock/refresh/sizzle/sonnet/ukulele/zorro,
            cartoonify, pixelate, saturation, blur, sepia, grayscale, vignette - you can add :value (e.g. 20)

        more info:
            cloudinary docs: https://cloudinary.com/documentation/transformation_reference
    """

    background: str = ""
    aspect_ratio: str = ""
    gravity: str = ""
    angle: int = 0
    width: int = 0
    height: int = 0
    crop: str = ""
    effects: list[str] = []


class TagIn(BaseModel):
    """
    Data model for enter tags.

    Attributes:
        tag_name (str): The name of the tag.
    """

    tag_name: str = Field(max_items=MAX_TAG_NAME_LENGTH)


class TagOut(TagIn):
    """
    Data model for tags.
    Inherits from TagIn.

    Attributes:
        id (int): The unique identifier of the tag.
    """

    id: int

    class Config:
        from_attributes = True


class PhotoOut(BaseModel):
    """
    Data model for retrieving photos.

    Attributes:
        id (int): The unique identifier of the photo.
        file_path (str): The url to the photo.
        qr_path (str): The url to the qr code leading to the photo.
        transformation (Dict[str, str]): The transformation of the photo.
        description (str): The description of the photo.
        upload_date (datetime): The date the photo was uploaded.
    """

    id: int
    file_path: str
    qr_path: str
    description: str
    tags: list[TagOut]
    transformation: Dict[str, list] | None = None
    upload_date: datetime

    class Config:
        from_attributes = True


class PhotoSearchOut(BaseModel):
    """
    Data model for returning photos for all app users (without transformation).

    Attributes:
        id (int): The unique identifier of the photo.
        file_path (str): The url to the photo.
        qr_path (str): The url to the qr code leading to the photo.
        description (str): The description of the photo.
        tags (list[TagOut]): The tags of the photo.
        upload_date (datetime): The date the photo was uploaded.
    """
    id: int
    file_path: str
    qr_path: str
    description: str
    tags: list[TagOut]
    upload_date: datetime

    class Config:
        from_attributes = True
