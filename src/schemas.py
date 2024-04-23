from pydantic import BaseModel, Field, EmailStr
from typing import Optional



class UserIn(BaseModel):
    '''
    Data model for creating new users.

    Attributes:
        username (str): The username of the user. Must be between 4 and 16 characters.
        email (str): The email address of the user.
        password (str): The password of the user. Must be between 6 and 10 characters.
    
    '''
    
    username: str = Field(min_length=4, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)
    role: Optional[str] = None



class UserOut(BaseModel):
    '''
    Data model for retrieving users.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        avatar (str): The avatar URL of the user.
    '''

    id: int
    username: str
    email: str
    avatar: str = "default_avatar.jpg"


    class Config:
        from_attributes = True

class TokenModel(BaseModel):
    '''
    Data model for tokens.

    Attributes:
        access_token (str): The access token.
        refresh_token (str): The refresh token.
        token_type (str): The type of token.
    '''
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    '''
    Data model for requesting email confirmation.

    Attributes:
        email (EmailStr): The email address for which confirmation is requested.
    
    '''
    
    email: EmailStr