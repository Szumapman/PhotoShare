from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository import users as users_repository
from src.database.db import get_db
from src.schemas import UserPublicProfile
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserPublicProfile)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieve a user's profile based on their email address.

    Args:
        user_id (int): The id of the user whose profile is to be retrieved.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        UserProfile: The user's profile information if found.
    """
    return await users_repository.get_user_public_profile(user_id, db)
