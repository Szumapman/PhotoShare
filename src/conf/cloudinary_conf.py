import cloudinary
from src.conf.config import settings


CLOUDINARY_CONFIG = cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

CLOUDINARY_PARAMS = {
    "photo_public_id_prefix": "PhotoShare",
    "qr_public_id_prefix": "PhotoShare/qr-codes",
}
