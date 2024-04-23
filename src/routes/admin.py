from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.repository import users as repository_users
from src.database.db import get_db
from schemas import UserIn, UserOut
from src.services.auth import auth_service

router = APIRouter(prefix="/admin", tags=["admin"])

def is_admin(user: UserOut = Depends(auth_service.get_current_user)):
    """
    Check if the current user is an admin.

    Args:
        user (UserOut): The currently authenticated user.

    Raises:
        HTTPException: If the user is not an admin.
    """

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")

@router.post("/create_moderator")
async def create_moderator(user_data: UserIn, db: Session = Depends(get_db), current_user: UserOut = Depends(is_admin)):
    """
    Create a new user with the specified role.

    Args:
        user_data (UserIn): Data of the new user to be created.
        db (Session): The database session.
        current_user (UserOut): The currently authenticated user.

    Returns:
        UserOut: Data of the newly created user.

    Raises:
        HTTPException: If the user creating the new user is not an admin.
    """
    user_data.role = "moderator"
    new_user = await repository_users.create_user(user_data, db)
    return new_user