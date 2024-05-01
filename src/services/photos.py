from io import BytesIO

import qrcode
from fastapi import HTTPException, status, File
import cloudinary
import cloudinary.uploader

from src.conf.config import CLOUDINARY_CONFIG


async def upload_photo(file: File) -> str:
    """
    Uploads a photo to Cloudinary.

    Args:
        file (File): File to be uploaded.

    Returns:
        str: URL of the uploaded photo.
    """
    upload_result = cloudinary.uploader.upload(
        file.file,
        public_id_prefix="PhotoShare",
        overwrite=True,
    )
    return upload_result["url"]


async def create_qr_code(photo_url: str) -> str:
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(photo_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_upload = cloudinary.uploader.upload(
            qr_buffer,
            public_id_prefix="PhotoShare/qr-codes",
            overwrite=True,
        )
        qr_url = qr_upload["url"]
        return qr_url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
