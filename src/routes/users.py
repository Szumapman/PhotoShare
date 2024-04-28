from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository import users as users_repository
from src.database.db import get_db
from src.schemas import UserProfile
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{email}", response_model=UserProfile)
async def get_user_profile(
    email: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    """
    Retrieve a user's profile based on their email address.

    Args:
        email (str): The email address of the user whose profile is to be retrieved.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        UserProfile: The user's profile information if found.

    Raises:
        HTTPException: If the user's profile is not found, returns a 404 Not Found error.
    """
    user_profile = await users_repository.get_user_profile(email, db)
    if user_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_profile