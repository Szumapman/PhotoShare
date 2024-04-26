from sqlalchemy.orm import Session

from src.database.models import Photo
from src.schemas import PhotoOut


async def upload_photo(file_path: str, user_id: int, db: Session):
    new_photo = Photo(
        file_path=file_path,
        description="na razie nie ma",
        user_id=user_id,
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return PhotoOut(
        id=new_photo.id,
        file_path=new_photo.file_path,
        description=new_photo.description,
        upload_date=new_photo.upload_date,
    )
