from io import BytesIO

import qrcode
from fastapi import HTTPException, status, File
import cloudinary
import cloudinary.uploader

from src.conf.config import CLOUDINARY_CONFIG, CLOUDINARY_PARAMS
from src.schemas import PhotoOut, TransformationParameters


async def _get_cloudinary_public_ip(url: str) -> str:
    return url.split("/")[-1].split(".")[0]


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
        public_id_prefix=CLOUDINARY_PARAMS["photo_public_id_prefix"],
        overwrite=True,
    )
    return upload_result["url"]


async def delete_from_cloudinary(photo: PhotoOut):
    photo_public_id = f"{CLOUDINARY_PARAMS['photo_public_id_prefix']}/{await _get_cloudinary_public_ip(photo.file_path)}"
    cloudinary.uploader.destroy(photo_public_id, invalidate=True)
    print(f"Deleted {photo_public_id}")
    qrcode_public_id = f"{CLOUDINARY_PARAMS['qr_public_id_prefix']}/{await _get_cloudinary_public_ip(photo.qr_path)}"
    cloudinary.uploader.destroy(qrcode_public_id, invalidate=True)
    print(f"Deleted {qrcode_public_id}")


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
            public_id_prefix=CLOUDINARY_PARAMS["qr_public_id_prefix"],
            overwrite=True,
        )
        qr_url = qr_upload["url"]
        return qr_url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def transform_photo(
    photo: PhotoOut, transformation_params: TransformationParameters
) -> (str, list[str]):

    """
    Function to perform transformations on a photo.

    Args:
         photo (PhotoOut): Photo to be transformed.
         transformation_params (TransformationParameters): Transformation parameters.

    Returns:
        tuple (str, list[dict]): URL of the transformed photo.
    """
    params = []
    if transformation_params.width:
        params.append({"width": transformation_params.width})
    if transformation_params.height:
        params.append({"height": transformation_params.height})
    if transformation_params.crop:
        params.append({"crop": transformation_params.crop})
    if transformation_params.effects:
        for effect in transformation_params.effects:
            params.append({"effect": effect})
    photo_public_id = f"{CLOUDINARY_PARAMS['photo_public_id_prefix']}/{await _get_cloudinary_public_ip(photo.file_path)}"
    transform_photo_url = cloudinary.utils.cloudinary_url(
        photo_public_id, transformation=params
    )[0]
    return transform_photo_url, params
