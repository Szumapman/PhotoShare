import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import Photo, Tag, PhotoTag
from src.schemas import PhotoOut, UserOut
from src.repository import photos as photos_repository


class TestTags(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = UserOut(
            id=1,
            username="user",
            email="test@email.com",
            role="standard",
        )

    async def test_upload_photo_with_tags(self):
        tags = ["tag1", "tag2"]
        new_photo_data = {
            "file_path": "test_file_path",
            "description": "test",
            "tags": tags,
        }
        new_photo = PhotoOut(
            id=1,
            file_path=new_photo_data["file_path"],
            description=new_photo_data["description"],
            upload_date=datetime.now(),
        )
        self.session.add.return_value = None
        result = await photos_repository.upload_photo(
            file_path=new_photo_data["file_path"],
            user_id=self.user.id,
            description=new_photo_data["description"],
            tags=new_photo_data["tags"],
            db=self.session,
        )
        self.assertEqual(result, new_photo)

    async def test_upload_photo_with_duplicate_tags(self):
        tags = ["tag1", "tag1", "tag2"]
        new_photo_data = {
            "file_path": "test_file_path",
            "description": "test",
            "tags": tags,
        }
        new_photo = PhotoOut(
            id=1,
            file_path=new_photo_data["file_path"],
            description=new_photo_data["description"],
            upload_date=datetime.now(),
        )
        self.session.add.return_value = None
        result = await photos_repository.upload_photo(
            file_path=new_photo_data["file_path"],
            user_id=self.user.id,
            description=new_photo_data["description"],
            tags=new_photo_data["tags"],
            db=self.session,
        )
        self.assertEqual(result, new_photo)

    async def test_upload_photo_with_existing_tags(self):
        existing_tag = Tag(id=1, tag_name="existing_tag")
        self.session.query().filter().first.return_value = existing_tag
        new_photo_data = {
            "file_path": "test_file_path",
            "description": "test",
            "tags": ["existing_tag"],
        }
        new_photo = PhotoOut(
            id=1,
            file_path=new_photo_data["file_path"],
            description=new_photo_data["description"],
            upload_date=datetime.now(),
        )
        self.session.add.return_value = None
        result = await photos_repository.upload_photo(
            file_path=new_photo_data["file_path"],
            user_id=self.user.id,
            description=new_photo_data["description"],
            tags=new_photo_data["tags"],
            db=self.session,
        )
        self.assertEqual(result, new_photo)

    async def test_delete_photo_with_tags(self):
        photo_id = 1
        photo_tags = [
            PhotoTag(photo_id=photo_id, tag_id=1),
            PhotoTag(photo_id=photo_id, tag_id=2),
        ]
        photo = Photo(id=photo_id, user_id=1)
        self.session.query().filter().first.return_value = photo
        self.session.query().filter().all.return_value = photo_tags
        result = await photos_repository.delete_photo(
            photo_id=photo_id, user=self.user, db=self.session
        )
        self.assertEqual(result, photo)
        self.session.delete.assert_called_once_with(photo)
        self.assertEqual(self.session.delete.call_count, len(photo_tags) + 1)

    async def test_delete_photo_with_no_tags(self):
        photo = Photo(id=1, user_id=1)
        self.session.query().filter().first.return_value = photo
        self.session.query().filter().all.return_value = []
        result = await photos_repository.delete_photo(
            photo_id=1, user=self.user, db=self.session
        )
        self.assertEqual(result, photo)
        self.session.delete.assert_called_once_with(photo)
