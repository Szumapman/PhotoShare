from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository import users as users_repository
from src.database.db import get_db
from src.schemas import UserIn, UserOut
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/update/me", response_model=UserOut)
async def update_users_me(
    body: UserIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    """
    Update the profile of the currently authenticated user.

    Args:
        body (UserIn): The updated user data.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        UserOut: The updated user profile.

    Raises:
        HTTPException: If there is an issue with updating the user profile.
    """
    user = await users_repository.update_users_me(current_user, body, db)
    return user