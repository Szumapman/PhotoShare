import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Photo, User
from src.repository.photos import (
    delete_photo,
)

class TestPhotos(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_delete_photo_found(self):
        photo = Photo()
        self.session.query().filter().first.return_value = photo
        result = await delete_photo(photo_id=1, user=self.user, db=self.session)
        self.assertEqual(result, photo)

    async def test_delete_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_photo(photo_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()