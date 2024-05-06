import unittest
from datetime import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Photo
from src.schemas import PhotoOut, UserOut, PhotoSearchOut
from src.repository import photos as photos_repository


class TestPhotos(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = UserOut(
            id=1,
            username="user",
            email="test@email.com",
            role="standard",
        )

    async def test_get_photo_found(self):
        photo = PhotoOut(
            id=1,
            file_path="test_file_path",
            qr_path="test_qr_path",
            description="test",
            tags=[],
            transformation=None,
            upload_date=datetime.now(),
        )
        self.session.query().filter().first.return_value = photo
        result = await photos_repository.get_photo_by_id(photo_id=1, db=self.session)
        self.assertEqual(result, photo)

    async def test_get_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await photos_repository.get_photo_by_id(photo_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_delete_photo_found(self):
        photo = Photo(id=1, user_id=1)
        self.session.query().filter().first.return_value = photo
        result = await photos_repository.delete_photo(
            photo_id=1, user=self.user, db=self.session
        )
        self.assertEqual(result, photo)

    async def test_delete_photo_as_admin(self):
        photo = Photo(id=1, user_id=1)
        self.session.query().filter().first.return_value = photo
        user = UserOut(
            id=2,
            username="user",
            email="test@email.com",
            password="testPass1",
            role="admin",
        )
        result = await photos_repository.delete_photo(
            photo_id=1, user=user, db=self.session
        )
        self.assertEqual(result, photo)

    async def test_delete_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await photos_repository.delete_photo(
                photo_id=1, user=self.user, db=self.session
            )
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "Photo not found")

    async def test_delete_photo_unauthorized(self):
        photo = Photo(id=1, user_id=2)
        self.session.query().filter().first.return_value = photo
        with self.assertRaises(HTTPException) as context:
            await photos_repository.delete_photo(
                photo_id=1, user=self.user, db=self.session
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            context.exception.detail, "Only owner of the photo or admin can delete it."
        )

    async def test_get_photos(self):
        photos = [
            PhotoSearchOut(
                id=1,
                file_path="path/to/photo2.jpg",
                qr_path="path/to/qr_photo2.jpg",
                description="Sunset view",
                upload_date=datetime(2021, 1, 1),
                tags=[],
            ),
            PhotoSearchOut(
                id=2,
                file_path="path/to/photo2.jpg",
                qr_path="path/to/qr_photo2.jpg",
                description="Sunset view",
                upload_date=datetime(2021, 1, 2),
                tags=[],
            ),
            PhotoSearchOut(
                id=3,
                file_path="path/to/photo3.jpg",
                qr_path="path/to/qr_photo3.jpg",
                description="Nature and wildlife on mountain",
                upload_date=datetime(2021, 1, 3),
                tags=[],
            ),
            # PhotoO(id=1, user_id=1),
            # Photo(id=2, user_id=2),
            # Photo(id=3, user_id=1),
        ]
        self.session.query.return_value.all.return_value = photos
        result = await photos_repository.get_photos(db=self.session)
        self.assertEqual(len(result), len(photos))
        self.assertEqual(result[0].id, photos[0].id)
        self.assertEqual(result[1].id, photos[1].id)

    async def test_get_photo_empty(self):
        self.session.query().return_value.all.return_value = []
        result = await photos_repository.get_photos(db=self.session)
        self.assertEqual(len(result), 0)
