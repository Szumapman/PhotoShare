import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import Photo
from src.schemas import PhotoOut, UserOut
from src.repository.photos import search_photos


class TestPhotos(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

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
                user_id=self.users[0].id
            ),
            Photo(
                id=2, file_path="path/to/photo2.jpg",
                description="Sunset view",
                upload_date=datetime(2021, 1, 2),
                user_id=self.users[0].id
            ),
            Photo(
                id=3, file_path="path/to/photo3.jpg",
                description="Nature and wildlife on mountain",
                upload_date=datetime(2021, 1, 3),
                user_id=self.users[2].id
            ),
        ]

        query_mock = MagicMock()
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = self.photos
        self.session.query.return_value = query_mock

    async def test_search_photos_with_empty_query(self):
        with patch('sqlalchemy.orm.query.Query.all', MagicMock(return_value=self.photos)):
            result = await search_photos(query=None, sort_by="date", db=self.session)
            self.assertEqual(len(result), len(self.photos))

    async def test_search_photos_with_description_query_sorted_by_date(self):
        with patch('sqlalchemy.orm.query.Query.filter', MagicMock(return_value=self.session.query())):
            with patch('sqlalchemy.orm.query.Query.order_by', MagicMock(return_value=self.session.query())):
                with patch('sqlalchemy.orm.query.Query.all', MagicMock(return_value=self.photos)):
                    result = await search_photos(query="mountain", sort_by="date", db=self.session)
                    self.assertTrue(all("mountain" in photo.description for photo in result))


if __name__ == '__main__':
    unittest.main()
