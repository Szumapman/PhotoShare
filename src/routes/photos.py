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
from src.database.models import User, Photo
from src.schemas import PhotoOut, UserOut, TransformationParameters
from src.services.auth import auth_service
from src.repository import photos as photos_repository
from src.services import photos as photos_services
from src.conf.constant import MAX_DESCRIPTION_LENGTH, MAX_TAG_NAME_LENGTH

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/", response_model=PhotoOut)
async def upload_photo(
    file: UploadFile = File(),
    description: str = Form(""),
    tags: list[str] = Form([]),
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> PhotoOut:
    """
    Uploads a new photo to the database.

    Args:
        file (UploadFile): A file to be uploaded.
        description (str): The description of the photo.
        tags (list[str]): A list of tags.
        current_user (UserOut): The current user.
        db (Session): A database session.

    Returns:
          PhotoOut: The uploaded photo.

    Raises:
          HTTPException: If the description or tag_name are too long, or if you try to add to many tags.
    """
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Description must be less than {MAX_DESCRIPTION_LENGTH} characters",
        )
    tags = tags[0].split(",")
    if len(tags) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many tags provided. You can use max of 5 tags.",
        )
    for tag in tags:
        if len(tag) > MAX_TAG_NAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag name must be less than {MAX_TAG_NAME_LENGTH} characters.",
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


@router.post("/transformation/{photo_id}", response_model=PhotoOut)
async def transform_photo(
    photo_id: int,
    transformation_params: TransformationParameters,
    current_user: UserOut = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a photo transformation

    Args:
         photo_id (int): The ID of the photo to be transformed.
         transformation_params (TransformationParameters): The transformation parameters (more info in Schemas.py).
         current_user (UserOut): An instance of User representing the authenticated user.
         db (Session): Database session.

    Returns:
        PhotoOut: The transformed photo object

    Raises:
        HTTPException: If the specified photo is not found in the database or action is not performed by photo owner.
    """
    photo = await photos_repository.get_photo_by_id(photo_id, db)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    if photo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the current authenticated user is allowed to perform the transformation.",
        )
    transform_photo_url, params = await photos_services.transform_photo(
        photo, transformation_params
    )
    photo = await photos_repository.add_transformation(
        photo, transform_photo_url, params, db
    )
    return photo

@router.get("/")
async def download_all_photos(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
    ):
    """
    Downloading the list of all photos uploaded by a specific user.

    Parameters:
    - user_id (int): The ID of the user whose photos are to be downloaded.
    - db (Session): Database session dependency.
    - current_user (User): Current user dependency.

    Raises:
    - HTTPException:
        - 404 NOT FOUND - If the specified user does not exist or if there are no photos uploaded by the user.
        - 401 UNAUTHORIZED - If the user is not authenticated.

    Returns:
        dict: A dictionary containing the list of photos uploaded by the user. Each photo is represented as a dictionary with keys 'photo id' and 'photo file path'.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in to access to photos list")

    photos = db.query(Photo).filter(Photo.user_id == user_id).all()
    if not photos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    photos_json = [{"photo id": photo.id, "photo file path": photo.file_path} for photo in photos]
    return {"photos": photos_json}
