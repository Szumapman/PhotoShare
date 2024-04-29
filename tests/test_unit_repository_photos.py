import unittest
from datetime import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.schemas import PhotoOut
from src.repository.photos import (
    get_photo_by_id,
)


class TestPhotos(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_photo_found(self):
        photo = PhotoOut(
            id=1,
            file_path="test_file_path",
            description="test",
            upload_date=datetime.now(),
        )
        self.session.query().filter().first.return_value = photo
        result = await get_photo_by_id(photo_id=1, db=self.session)
        print(result.file_path)
        self.assertEqual(result, photo)

    async def test_get_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_photo_by_id(photo_id=1, db=self.session)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
