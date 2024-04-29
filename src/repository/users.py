from libgravatar import Gravatar
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import User
from src.schemas import UserIn, UserOut
from src.services.auth import auth_service


async def count_users(db: Session):
    return db.query(User).count()


async def get_user_by_email(email: str, db: Session) -> UserOut:
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


async def create_user(body: UserIn, db: Session) -> User:
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
    return new_user


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
    return user


async def set_user_role(user: UserOut, email: str, role: str, db: Session) -> UserOut:
    """
    Set the role of the user with the given email address in the database.
    Args:
        user (UserOut): The user who wants to set the role (must be admin).
        email (str): The email address of the user whose role will be set.
        role (str): The new role.
        db (Session): The database session.
    Returns:
        UserOut: The user with the updated role.
    Raises:
        HTTPException:
    """
    if user.role == "admin":
        user = await get_user_by_email(email, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email:{email} not found",
            )
        user.role = role
        db.commit()
        db.refresh(user)
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Only admin users are allowed to set the role of users",
    )


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
            id=user_id,
            username=user.username,
            password=user.password,
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
