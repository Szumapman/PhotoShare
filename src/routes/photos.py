from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import PhotoOut, UserOut
from src.services.auth import auth_service
from src.repository import photos as photos_repository
from src.services import photos as photos_services

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/", response_model=PhotoOut)
async def upload_photo(
    file: UploadFile = File(),
    description: str = Form(""),
    tags: list[str] = Form([]),
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> PhotoOut:
    tags = tags[0].split(",")
    if len(tags) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many tags provided. You can use max of 5 tags.",
        )
    photo_url = await photos_services.upload_photo(file)
    qr_code_url = await photos_services.create_qr_code(photo_url)
    new_photo = await photos_repository.upload_photo(
        photo_url, qr_code_url, current_user.id, description, tags, db
    )
    return new_photo


@router.get("/{photo_id}", response_model=PhotoOut)
async def get_photo(
    photo_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a photo by its ID.

    Args:
        photo_id (int): The photo ID.
        current_user (User): The current authenticated user.
        db (Session): Database session.

    Returns:
        PhotoOut: The photo matching the provided photo ID.
    """
    photo = await photos_repository.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/download/{photo_id}")
async def download_photo(
    photo_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> str:
    """
    Download a photo by its ID.

    Args:
        photo_id (int): The photo ID.
        current_user (User): The current authenticated user.
        db (Session): Database session.

    Returns:
        str: with url to the photo.
    """
    photo = await photos_repository.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo.file_path


@router.patch("/description/{photo_id}", response_model=PhotoOut)
async def edit_photo_description(
    photo_id: int,
    description: str = Form(),
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Edit photo description

    Args:
        photo_id (int): Photo ID
        description (str): new description
        current_user (User): Current authenticated user
        db (Session): Database

    Returns:
        PhotoOut: The updated photo object
    """
    updated_photo = photos_repository.update_photo_description(
        photo_id, description, current_user, db
    )
    if not updated_photo:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update photo description",
        )
    return updated_photo


@router.delete("/{photo_id}", response_model=PhotoOut)
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(auth_service.get_current_user),
):
    """
    Delete a photo from the database if it belongs to the authenticated user.

    Args:
        photo_id (int): The ID of the photo to be deleted.
        db (Session): The database session.
        current_user (UserOut): An instance of User representing the authenticated user.

    Returns:
        PhotoOut: The deleted photo object.

    Raises:
        HTTPException: If the specified photo is not found in the database.
    """
    photo = await photos_repository.delete_photo(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    await photos_services.delete_from_cloudinary(photo)
    return photo
