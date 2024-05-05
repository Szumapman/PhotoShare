from io import BytesIO

import qrcode
from fastapi import HTTPException, status, File
import cloudinary
import cloudinary.uploader

from src.conf.cloudinary_conf import CLOUDINARY_CONFIG, CLOUDINARY_PARAMS
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
    # validate_transformation_params(transformation_params)

    params = []
    if transformation_params.background:
        params.append({"background": transformation_params.background})
    if transformation_params.angle:
        params.append({"angle": transformation_params.angle})
    if transformation_params.width and transformation_params.width > 0:
        params.append({"width": transformation_params.width})
    if transformation_params.height and transformation_params.height > 0:
        params.append({"height": transformation_params.height})
    if transformation_params.crop:
        params.append({"crop": transformation_params.crop})
    if transformation_params.effects:
        for effect in transformation_params.effects:
            params.append({"effect": effect})
    if not params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid transformations were provided.",
        )
    photo_public_id = f"{CLOUDINARY_PARAMS['photo_public_id_prefix']}/{await _get_cloudinary_public_ip(photo.file_path)}"
    transform_photo_url = cloudinary.utils.cloudinary_url(
        photo_public_id, transformation=params
    )[0]
    return transform_photo_url, params


def validate_transformation_params(
    transformation_params: TransformationParameters,
) -> None:
    """
    Validate transformation parameters.

    Args:
         transformation_params (dict): Transformation parameters.

    Raises:
        ValueError: If transformation parameters are invalid.
    """

    if (
        not isinstance(transformation_params.width, int)
        or transformation_params.width <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Width must be a positive integer",
        )

    if (
        not isinstance(transformation_params.height, int)
        or transformation_params.height <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Height must be a positive integer",
        )

    if not transformation_params.crop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Crop mode cannot be empty",
        )
    if (
        len(transformation_params.effects) == 0
    ):  # 'if not transformation_params.effects' didn't work
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Effects cannot be empty",
        )

    valid_crop_modes = {
        "fill",
        "lfill",
        "fill_pad",
        "crop",
        "thumb",
        "auto",
        "scale",
        "fit",
        "limit",
        "mfit",
        "pad",
        "lpad",
        "mpad",
        "imagga_scale",
        "imagga_crop",
    }
    if transformation_params.crop not in valid_crop_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid crop mode. Supported modes are: "
            + ", ".join(valid_crop_modes),
        )

    valid_effects = {
        "art:al_dente",
        "art:athena",
        "art:audrey",
        "art:aurora",
        "art:daguerre",
        "art:eucalyptus",
        "art:fes",
        "art:frost",
        "art:hairspray",
        "art:hokusai",
        "art:incognito",
        "art:linen",
        "art:peacock",
        "art:primavera",
        "art:quartz",
        "art:red_rock",
        "art:refresh",
        "art:sizzle",
        "art:sonnet",
        "art:ukulele",
        "art:zorro",
        "cartoonify",
        "pixelate:value",
        "saturation:value",
        "blur:value",
        "sepia",
        "grayscale",
        "vignette",
    }

    if len(transformation_params.effects) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can select up to 5 effects.",
        )
    if any(effect not in valid_effects for effect in transformation_params.effects):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid effect. Supported modes are: " + ", ".join(valid_effects),
        )
