import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import Photo, Tag, PhotoTag
from src.repository.users import admin_moderator_search_users_with_photos
from src.schemas import PhotoOut, UserOut


class TestSearchUsersWithPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.query_mock = MagicMock()
        self.session.query.return_value = self.query_mock
        self.query_mock.join.return_value = self.query_mock
        self.query_mock.filter.return_value = self.query_mock
        self.query_mock.distinct.return_value = self.query_mock
        self.query_mock.group_by.return_value = self.query_mock
        self.query_mock.order_by.return_value = self.query_mock

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

    async def test_search_by_username(self):
        self.query_mock.all.return_value = [self.users[0]]
        result = await admin_moderator_search_users_with_photos("user1", None, None, self.session)
        self.assertEqual(self.query_mock.filter.call_count, 2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].username, "user1")

    async def test_search_by_description(self):
        self.query_mock.all.return_value = [self.users[1]]
        result = await admin_moderator_search_users_with_photos(None, "sunset", None, self.session)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].username, "user2")

    async def test_search_by_tag(self):
        self.query_mock.all.return_value = [self.users[1]]
        result = await admin_moderator_search_users_with_photos(None, None, "nature", self.session)
        self.query_mock.join.assert_called()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].username, "user2")

    async def test_no_results(self):
        self.query_mock.all.return_value = []
        result = await admin_moderator_search_users_with_photos("nonexistent", None, None, self.session)
        self.assertEqual(len(result), 0)

    async def test_no_filters(self):
        self.query_mock.all.return_value = self.users
        result = await admin_moderator_search_users_with_photos(None, None, None, self.session)
        self.assertEqual(len(result), 3)


if __name__ == '__main__':
    unittest.main()
