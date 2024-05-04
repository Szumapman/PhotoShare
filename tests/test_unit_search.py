import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import Photo, Tag, PhotoTag
from src.schemas import PhotoOut, UserOut
from src.repository.photos import search_photos


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.query_mock = MagicMock()
        self.session.query.return_value = self.query_mock
        self.query_mock.join.return_value = self.query_mock
        self.query_mock.filter.return_value = self.query_mock
        self.query_mock.order_by.return_value = self.query_mock
        self.query_mock.distinct.return_value = self.query_mock

        self.users = [
            UserOut(
                id=1, username="user1", email="user1@email.com",
                role="standard", avatar="path/to/avatar1", is_active=True
            ),
            UserOut(
                id=2, username="user2", email="user2@email.com",
                role="standard", avatar="path/to/avatar2", is_active=True
            ),
            UserOut(
                id=3, username="user3", email="user3@email.com",
                role="standard", avatar="path/to/avatar3", is_active=True)
        ]
        self.photos = [
            Photo(
                id=1, file_path="path/to/photo1.jpg",
                description="Beautiful mountain",
                upload_date=datetime(2021, 1, 1),
                user_id=1
            ),
            Photo(
                id=2, file_path="path/to/photo2.jpg",
                description="Sunset view",
                upload_date=datetime(2021, 1, 2),
                user_id=1
            ),
            Photo(
                id=3, file_path="path/to/photo3.jpg",
                description="Nature and wildlife on mountain",
                upload_date=datetime(2021, 1, 3),
                user_id=3
            ),
        ]
        self.tags = [
            Tag(id=1, tag_name="mountain"),
            Tag(id=2, tag_name="sunset"),
            Tag(id=3, tag_name="nature"),
        ]
        self.photo_tags = [
            PhotoTag(photo_id=1, tag_id=1),
            PhotoTag(photo_id=2, tag_id=2),
            PhotoTag(photo_id=3, tag_id=3),
        ]

    async def test_search_photos_with_query(self):
        self.query_mock.all.return_value = [self.photos[0]]
        result = await search_photos("mountain", "date", self.session)
        self.query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].description, "Beautiful mountain")

    async def test_search_photos_no_results(self):
        self.query_mock.all.return_value = []
        result = await search_photos("ocean", "date", self.session)
        self.assertEqual(len(result), 0)

    async def test_search_photos_sort_by_date(self):
        self.query_mock.all.return_value = sorted(self.photos, key=lambda x: x.upload_date, reverse=True)
        result = await search_photos(None, "date", self.session)
        self.assertTrue(all(result[i].upload_date >= result[i + 1].upload_date for i in range(len(result) - 1)))

    async def test_search_photos_invalid_sort_option(self):
        with self.assertRaises(ValueError):
            await search_photos("mountain", "invalid_sort_option", self.session)


if __name__ == '__main__':
    unittest.main()
