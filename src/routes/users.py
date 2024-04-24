import pickle

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service, Auth
from src.conf.config import settings
from src.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


def is_admin(user: UserOut = Depends(auth_service.get_current_user)):
    '''
      Middleware to check if the user has admin privileges.

      Args:
          user (UserOut): The currently authenticated user.

      Raises:
          HTTPException: If the user does not have admin privileges.
    '''

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied, admin role required")


def is_moderator_or_admin(user: UserOut = Depends(auth_service.get_current_user)):
    '''
        Middleware to check if the user has moderator or admin privileges.

        Args:
            user (UserOut): The currently authenticated user.

        Raises:
            HTTPException: If the user does not have moderator or admin privileges.
    '''

    if user.role not in ["moderator", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied, moderator or admin role required")


# @router.get("/me", response_model=UserOut)
# async def read_users_me(current_user: UserOut = Depends(auth_service.get_current_user)):
#     '''
#     Retrieve the details of the currently authenticated user.
#
#     Args:
#         current_user (User): The currently authenticated user.
#
#     Returns:
#         UserOut: Details of the currently authenticated user.
#     '''
#
#     return current_user


# @router.patch('/avatar', response_model=UserOut)
# async def update_avatar_user(file: UploadFile = File(), current_user: UserOut = Depends(auth_service.get_current_user),
#                              db: Session = Depends(get_db)):
#     '''
#     Update the avatar for the currently authenticated user.
#
#     Args:
#         file (UploadFile): The avatar image file to upload.
#         current_user (User): The currently authenticated user.
#         db (Session): The database session.
#
#     Returns:
#         UserOut: The updated details of the currently authenticated user.
#     '''
#
#     cloudinary.config(
#         cloud_name=settings.cloudinary_name,
#         api_key=settings.cloudinary_api_key,
#         api_secret=settings.cloudinary_api_secret,
#         secure=True
#     )
#
#     r = cloudinary.uploader.upload(file.file, public_id=f'PhotoShareApp/{current_user.username}', overwrite=True)
#     src_url = cloudinary.CloudinaryImage(f'PhotoShareApp/{current_user.username}') \
#         .build_url(width=250, height=250, crop='fill', version=r.get('version'))
#     user = await repository_users.update_avatar(current_user.email, src_url, db)
#     Auth.r.set(f"user:{user.email}", pickle.dumps(user))
#     return user

@router.get("/admin_only")
async def admin_only(current_user: UserOut = Depends(is_admin)):
    '''
       Endpoint accessible only to users with admin privileges.

       Args:
           current_user (UserOut, optional): The currently authenticated user with admin privileges.

       Returns:
           dict: A message indicating the user's admin access.
       '''

    return {"message": "You have admin access"}

@router.get("/moderator_or_admin")
async def moderator_or_admin(current_user: UserOut = Depends(is_moderator_or_admin)):
    '''
        Endpoint accessible to users with either moderator or admin privileges.

        Args:
            current_user (UserOut): The currently authenticated user with moderator or admin privileges.

        Returns:
            dict: A message indicating the user's moderator or admin access.
    '''

    return {"message": "You have moderator or admin access"}