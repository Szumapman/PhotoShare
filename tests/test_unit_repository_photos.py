import unittest
from datetime import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Photo
from src.schemas import PhotoOut, UserOut
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
            description="test",
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


if __name__ == "__main__":
    unittest.main()
