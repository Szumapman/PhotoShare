from typing import List
from sqlalchemy.orm import Session
from src.database.models import Photo


async def get_photo_file_path(file_path: str, db):
    return db.query(Photo).filter(Photo.file_path == file_path)


async def uplode_photo(id: int, url: int, db: Session):
    photo = await get_photo_file_path(id, db)
    if photo:
        return photo
    else:
        new_photo = Photo(file_path=url)
        db.add(new_photo)
        db.commit()
        return new_photo


async def remove_photo(id: int, db: Session) -> Photo | None:
    photo = db.query(Photo).filter(Photo.id == id).first
    if photo:
        db.delate(photo)
        db.commit()
    return photo
