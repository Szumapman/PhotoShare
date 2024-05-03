import unittest

from fastapi import HTTPException, status

from src.repository.tags import (
    get_tags,
    add_tag,
    update_tag,
    delete_tag,
    _get_tag,
    _get_photo,
)
from src.database.models import Base, User, Photo, Tag, PhotoTag
from src.schemas import UserIn, UserOut
from tests.db_test_config import engine, testing_session_local


class TestRepositoryTags(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(engine)
        self.db = testing_session_local()
        self.user_admin = User(
            username="user_admin",
            email="admin@email.com",
            password="pasS123!",
            confirmed=True,
            role="admin",
        )
        self.user_moderator = User(
            username="user_moderator",
            email="moderator@email.com",
            password="pasS123!",
            confirmed=True,
            role="moderator",
        )
        self.user = User(
            username="user",
            email="<EMAIL>",
            password="<PASSWORD>!",
            confirmed=True,
            role="standard",
        )
        self.photo_1 = Photo(
            file_path="photo_url",
            qr_path="qr_url",
            description="description",
            user_id=3,
        )
        self.photo_2 = Photo(
            file_path="photo_url",
            qr_path="qr_url",
            description="description",
            user_id=3,
        )
        self.photo_3 = Photo(
            file_path="photo_url",
            qr_path="qr_url",
            description="description",
            user_id=2,
        )
        self.tag_1 = Tag(tag_name="tag_1")
        self.tag_2 = Tag(tag_name="tag_2")
        self.tag_3 = Tag(tag_name="tag_3")
        self.tag_4 = Tag(tag_name="tag_4")
        self.tag_5 = Tag(tag_name="tag_5")
        self.tag_6 = Tag(tag_name="tag_6")
        self.db.add(self.user_admin)
        self.db.add(self.user_moderator)
        self.db.add(self.user)
        self.db.add(self.photo_1)
        self.db.add(self.photo_2)
        self.db.add(self.photo_3)
        self.db.add(self.tag_1)
        self.db.add(self.tag_2)
        self.db.add(self.tag_3)
        self.db.add(self.tag_4)
        self.db.add(self.tag_5)
        self.db.add(self.tag_6)
        self.db.add(PhotoTag(photo_id=1, tag_id=1))
        self.db.add(PhotoTag(photo_id=1, tag_id=2))
        self.db.add(PhotoTag(photo_id=1, tag_id=3))
        self.db.add(PhotoTag(photo_id=1, tag_id=4))
        self.db.add(PhotoTag(photo_id=2, tag_id=1))
        self.db.add(PhotoTag(photo_id=2, tag_id=5))
        self.db.add(PhotoTag(photo_id=2, tag_id=6))
        self.db.commit()

    def tearDown(self):
        self.db.close()

    async def test_add_tag_success(self):
        result = await add_tag(
            photo_id=1,
            tag_name="new_tag",
            user_id=3,
            db=self.db,
        )
