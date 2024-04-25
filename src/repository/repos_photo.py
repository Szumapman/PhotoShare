from sqlalchemy.orm import Session

from ..schemas.schemas import PhotoCreate, Photo, User


def upload_photo(db: Session, photo_data: PhotoCreate, user: User):
    db_photo = Photo(**photo_data.dict(), user_id=user.user_id)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def delete_photo(db: Session, photo_id: int, user: User):
    photo = db.query(Photo).filter(Photo.photo_id == photo_id, Photo.user_id == user.user_id).first()
    if photo:
        db.delete(photo)
        db.commit()
        return True
    return False


def description_photo(db: Session, photo_id: int, description: str, user: User):
    photo = db.query(Photo).filter(Photo.photo_id == photo_id, Photo.user_id == user.user_id).first()
    if photo:
        photo.description = description
        db.commit()
        return photo
    return None


def get_photo_link(db: Session, photo_id: int):
    photo = db.query(Photo).filter(Photo.photo_id == photo_id).first()
    if photo:
        return photo.file_path
    return None
