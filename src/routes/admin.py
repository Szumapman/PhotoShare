from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from fastapi import APIRouter, HTTPException, Depends, status
from src.services.auth import auth_service
from src.repository import users as repository_users
from src.schemas import UserOut, UserRole


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/", response_model=list[UserOut])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves all users from the database.

    Args:
        db (Session, optional): Database session dependency.
        current_user (User): Current authenticated user.

    Returns:

    Raises:
        HTTPException: 403 FORBIDDEN - If the current user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can get all users list.",
        )

    return await repository_users.get_users(db)


@router.post("/activ_status/{user_id}")
async def set_active_status(
    user_id: int,
    new_active_status: bool,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Only admins can deactivate users")
    user = await repository_users.set_user_is_active(user_id, new_active_status, db)
    return user


@router.patch("/set_role/{user_id}")
async def set_role(
    user_id: int,
    new_role: UserRole,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    """
    Updates the user's role

    Args:
        user_id (int): The id of the user to update
        new_role (UserRole): The new user role
        current_user (User): The current user
        db (Session): Database session

    Returns:
        UserOut: The updated user

    Raises:
        HTTPException: If the current user is not admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users are allowed to set the role of users",
        )
    return await repository_users.set_user_role(user_id, new_role.role, db)
