from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from fastapi import APIRouter, HTTPException, Depends, status, Query
from src.services.auth import auth_service
from src.repository import users as repository_users
from src.schemas import UserOut, UserRole, UserPublicProfile

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
async def index(
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    users = db.query(
        User.id, User.username, User.email, User.created_at, User.is_active
    ).all()
    users_json = [user._asdict() for user in users]
    return {"users": users_json}


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


@router.get("/users_with_photos", response_model=List[UserPublicProfile])
async def search_users_with_photos(
    username: Optional[str] = Query(None, description="Search by username"),
    description: Optional[str] = Query(None, description="Search by photo description"),
    tag: Optional[str] = Query(None, description="Search by photo tag"),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(auth_service.get_current_user),
) -> List[UserPublicProfile]:
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    users = await repository_users.admin_moderator_search_users_with_photos(username, description, tag, db)
    return users
