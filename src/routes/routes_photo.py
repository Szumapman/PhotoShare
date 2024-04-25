from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from ..repository import repos_photo as repos_photos
from ..database.db import get_db
from ..database.models import Photo
from ..schemas.schemas import PhotoCreate

router = APIRouter()


@router.post("/photos/", response_model=Photo)
async def upload_photo(photo: PhotoCreate, db: Session = Depends(get_db)):
    return repos_photos.upload_photo(db, photo) # dodac user


@router.delete("/photos/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    if not repos_photos.delete_photo(db, photo_id): # dodac user
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"ok": True}


@router.put("/photos/{photo_id}/description")
def update_photo_description(photo_id: int, description: str, db: Session = Depends(get_db)):
    photo = repos_photos.description_photo(db, photo_id, description) # dodac user
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found or access denied")
    return photo


@router.get("/photos/{photo_id}/download")
def download_photo(photo_id: int, db: Session = Depends(get_db)):
    file_path = repos_photos.get_photo_link(db, photo_id)
    if file_path is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(file_path)
