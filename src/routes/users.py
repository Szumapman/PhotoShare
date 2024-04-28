from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository import users as users_repository
from src.database.db import get_db
from src.schemas import UserProfileMe
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserProfileMe)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user)
    ):
    """
    Retrieve the profile information of the authenticated user.

    Args:
        current_user (User): An instance of the User model representing the authenticated user.

    Returns:
        UserProfileMe: An instance of UserProfileMe containing the profile information of the authenticated user.

    Raises:
        HTTPException: If the current user cannot be authenticated or if there is an error retrieving the user's profile information.
    """
    return current_user