from sqlalchemy.orm import Session

from ..database import models
from ..schemas import schemas


def upload_photo(db: Session, photo_data: schemas.PhotoCreate):
    db_photo = models.Photo(**photo_data.dict())
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def delete_photo(db: Session, photo_id: int):
    photo = db.query(models.Photo).filter(models.Photo.photo_id == photo_id).first()
    if photo:
        db.delete(photo)
        db.commit()
        return True
    return False


def update_photo_description(db: Session, photo_id: int, user_id: int, description: str):
    photo = db.query(models.Photo).filter(models.Photo.photo_id == photo_id, models.Photo.user_id == user_id).first()
    if photo:
        photo.description = description
        db.commit()
        return photo
    return None


def get_photo_file_path(db: Session, photo_id: int):
    photo = db.query(models.Photo).filter(models.Photo.photo_id == photo_id).first()
    if photo:
        return photo.file_path
    return None
