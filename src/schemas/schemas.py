from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date


class PhotoBase(BaseModel):
    file_path: str


class PhotoCreate(PhotoBase):
    pass


class Photo(PhotoBase):
    photo_id: int
    upload_date: datetime
    user_id: int
    tags: List[str] = []

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    comment_id: int
    date_posted: datetime
    user_id: int
    photo_id: int

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    tag_name: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    tag_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name_to_show: str


class UserCreate(UserBase):
    first_name: str
    last_name: str
    birth_date: date
    email: str
    phone_number: Optional[str] = None


class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True
