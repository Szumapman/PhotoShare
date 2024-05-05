from typing import Optional, List

from libgravatar import Gravatar
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import User, Photo, Tag
from src.schemas import UserIn, UserOut, UserPublicProfile
from src.services.auth import auth_service


async def count_users(db: Session):
    return db.query(User).count()


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieve a user from the database by their email address.

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The database session.

    Returns:
        UserOut: The user retrieved from the database.
    """
    user = db.query(User).filter(User.email == email).first()
    return user


async def create_user(body: UserIn, db: Session) -> UserOut:
    """
    Create a new user in the database.

    Args:
        body (UserIn): The input data for creating the user.
        db (Session): The database session.

    Returns:
        User: The newly created user.

    Raises:
        Exception: If an error occurs while fetching the avatar from Gravatar.
    """

    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    if avatar is None:
        pass
    new_user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        role=(
            "admin" if await count_users(db) == 0 else "standard"
        ),  # tworzenia admina jako pierwszego usera do czasu zrobienia skyptu
        avatar=avatar,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        avatar=new_user.avatar,
        is_active=new_user.is_active,
    )


async def update_token(user: UserOut, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a given user in the database.
    
    Args:
        user (User): The user for whom the refresh token will be updated.
        token (str | None): The new refresh token. If None, the token will be removed.
        db (Session): The database session.

    Returns:
        None
    """

    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:
    """
    Confirm the email address of the user with the given email  in the database.

    Args:
        email (str): The email address of the user to confirm.
        db (Session): The database session.

    Returns:
        None
    """

    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email:{email} not found",
        )
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> UserOut:
    """
    Update the avatar URL for the user with the given email address in the database.

    Args:
        email (str): The email address of the user whose avatar will be updated.
        url (str): The new avatar URL.
        db (Session): The database session.

    Returns:
        UserOut: The user with the updated avatar URL.
    """

    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email:{email} not found",
        )
    user.avatar = url
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        avatar=user.avatar,
        is_active=user.is_active,
    )


async def get_users(db: Session) -> list[UserOut]:
    """
    Retrieves all users from the database.

    Parameters:
    - db (Session): Database session dependency.

    Returns:
    list[UserOut]: The list of users.
    """
    return db.query(User).all()


async def set_user_role(user_id: int, role: str, db: Session) -> UserOut:
    """
    Set the role of the user with the given email address in the database.

    Args:
        user_id (int): The user id to set the role to.
        role (str): The new role.
        db (Session): The database session.

    Returns:
        UserOut: The user with the updated role.

    Raises:
        HTTPException: If not user with the given id
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found",
        )
    user.role = role
    db.commit()
    db.refresh(user)
    user_out = UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        avatar=user.avatar,
        is_active=user.is_active,
    )
    await auth_service.set_user_in_redis(user.email, user_out)
    return user_out


async def set_user_is_active(user_id: int, is_active: bool, db: Session) -> UserOut:
    """
    Set the active status of the user with the given user_id in the database.

    Args:
        user_id (int): The user who wants to set the active status.
        is_active (bool): Whether the user is active or not.
        db (Session): The database session.

    Returns:
        UserOut: The user with the updated active status.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        user_out = UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            avatar=user.avatar,
            is_active=is_active,
        )
        await auth_service.set_user_in_redis(user.email, user_out)
        return user_out
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found",
        )


async def get_user_public_profile(user_id: int, db: Session) -> UserPublicProfile:
    user_with_photo_count = (
        db.query(User.id, User.username, User.avatar)
        .filter(User.id == user_id)
        .outerjoin(Photo, User.id == Photo.user_id)
        .add_column(func.count(Photo.id).label("photo_count"))
        .group_by(User.id)
        .first()
    )
    if not user_with_photo_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} not found",
        )
    user_id, username, avatar, photo_count = user_with_photo_count
    return UserPublicProfile(
        id=user_id,
        username=username,
        avatar=avatar,
        photo_count=photo_count,
    )


async def update_current_user_profile(
        user: UserOut, new_user_data: UserIn, db: Session
) -> UserOut:
    """
    Update the current user in the database.

    Args:
        user (UserOut): The user to update.
        new_user_data (UserIn): New data for the user's profile.
        db (Session): The database session.

    Returns:
        UserOut: The updated user.
    """
    exist_user = db.query(User).filter(User.email == new_user_data.email).first()
    if exist_user and exist_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account with {new_user_data.email} already exists.",
        )
    updated_user = db.query(User).filter(User.id == user.id).first()
    if updated_user:
        updated_user.username = new_user_data.username
        updated_user.email = new_user_data.email
        updated_user.password = auth_service.get_password_hash(new_user_data.password)
        db.commit()
        db.refresh(updated_user)
        return updated_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id: {user.id} not found",
    )


async def admin_moderator_search_users_with_photos(
        username: Optional[str],
        description: Optional[str],
        tag: Optional[str],
        db: Session
) -> List[UserPublicProfile]:
    query = db.query(User).join(Photo, User.id == Photo.user_id).distinct()

    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if description:
        query = query.filter(Photo.description.ilike(f"%{description}%"))
    if tag:
        query = query.join(Photo.tags).filter(Tag.tag_name.ilike(f"%{tag}%"))

    query = query.group_by(User.id).order_by(User.created_at.desc())

    user_list = query.all()
    if not user_list:
        return []

    return [UserPublicProfile(
        id=user.id,
        username=user.username,
        avatar=user.avatar,
        photo_count=db.query(func.count(Photo.id)).filter(Photo.user_id == user.id).scalar()
    ) for user in user_list]
