from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from fastapi import APIRouter, HTTPException, Depends
from src.services.auth import auth_service


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
def index(
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


@router.post("/deactivate/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Only admins can deactivate users")
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        return {"message": "User deactivated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
