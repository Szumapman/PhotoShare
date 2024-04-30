import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Photo, User
from src.schemas import UserOut
from src.repository.photos import (
    delete_photo,
)


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = UserOut(
            id=1,
            username="user",
            email="test@email.com",
            password="testPass1",
            role="standard",
        )

    async def test_delete_photo_found(self):
        photo = Photo(id=1, user_id=1)
        self.session.query().filter().first.return_value = photo
        result = await delete_photo(photo_id=1, user=self.user, db=self.session)
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
        result = await delete_photo(photo_id=1, user=user, db=self.session)
        self.assertEqual(result, photo)

    async def test_delete_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await delete_photo(photo_id=1, user=self.user, db=self.session)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Photo not found")

    async def test_delete_photo_unauthorized(self):
        photo = Photo(id=1, user_id=2)
        self.session.query().filter().first.return_value = photo
        with self.assertRaises(HTTPException) as context:
            await delete_photo(photo_id=1, user=self.user, db=self.session)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(
            context.exception.detail, "Only owner of the photo or admin can delete it."
        )


if __name__ == "__main__":
    unittest.main()
