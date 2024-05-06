import unittest

from fastapi import HTTPException, status

from src.database.models import Base, User, Photo, Tag, PhotoTag
from tests.conftest import engine, testing_session_local
from src.repository.tags import (
    get_tags,
    add_tag,
    update_tag,
    delete_tag,
    _get_tag,
    _get_photo,
)


def check_tag_in_list_tags(result, tag_name):
    for tag in result:
        if tag.tag_name == tag_name:
            return True
    return False


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
        self.user_2 = User(
            username="user_2",
            email="<EMAIL>_2",
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
        self.new_tag_name = "new_tag"
        self.tag_1 = Tag(tag_name="tag_1")
        self.tag_2 = Tag(tag_name="tag_2")
        self.tag_3 = Tag(tag_name="tag_3")
        self.tag_4 = Tag(tag_name="tag_4")
        self.tag_5 = Tag(tag_name="tag_5")
        self.tag_6 = Tag(tag_name="tag_6")
        self.db.add(self.user_admin)
        self.db.add(self.user_moderator)
        self.db.add(self.user)
        self.db.add(self.user_2)
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
            tag_name=self.new_tag_name,
            user_id=3,
            db=self.db,
        )
        self.assertTrue(check_tag_in_list_tags(result, self.new_tag_name))

    async def test_add_tag_fail_wrong_user(self):
        with self.assertRaises(HTTPException) as context:
            result = await add_tag(
                photo_id=1,
                tag_name=self.new_tag_name,
                user_id=999,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, "Only the photo owner can add tags")

    async def test_add_tag_fail_tag_already_exist(self):
        await add_tag(
            photo_id=2,
            tag_name=self.new_tag_name,
            user_id=3,
            db=self.db,
        )
        with self.assertRaises(HTTPException) as context:
            result = await add_tag(
                photo_id=2,
                tag_name=self.new_tag_name,
                user_id=3,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "This photo already has this tag")

    async def test_add_tag_fail_too_much_tags(self):
        await add_tag(
            photo_id=1,
            tag_name=self.new_tag_name,
            user_id=3,
            db=self.db,
        )
        with self.assertRaises(HTTPException) as context:
            result = await add_tag(
                photo_id=1,
                tag_name="another_tag",
                user_id=3,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            context.exception.detail,
            "Photo tags can only have five tags, to add new tag you have to first delete another tag.",
        )

    async def test_update_tag_success(self):
        tag_update_name = "another_tag"
        result = await update_tag(
            photo_id=1,
            tag_id=1,
            tag_update_name=tag_update_name,
            current_user_id=3,
            db=self.db,
        )
        self.assertTrue(check_tag_in_list_tags(result, tag_update_name))
        self.assertFalse(check_tag_in_list_tags(result, self.tag_1.tag_name))

    async def test_update_tag_fail_wrong_user(self):
        with self.assertRaises(HTTPException) as context:
            await update_tag(
                photo_id=1,
                tag_id=1,
                tag_update_name="test",
                current_user_id=999,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            context.exception.detail, "Only the photo owner can update tags"
        )

    async def test_update_tag_fail_tag_already_exist(self):
        with self.assertRaises(HTTPException) as context:
            await update_tag(
                photo_id=1,
                tag_id=1,
                tag_update_name=self.tag_1.tag_name,
                current_user_id=3,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "This photo already has this tag")

    async def test_delete_tag_success(self):
        result = await delete_tag(
            photo_id=1,
            tag_id=1,
            user=self.user,
            db=self.db,
        )
        self.assertFalse(check_tag_in_list_tags(result, self.tag_1.tag_name))
        result = await delete_tag(
            photo_id=1,
            tag_id=2,
            user=self.user_admin,
            db=self.db,
        )
        self.assertFalse(check_tag_in_list_tags(result, self.tag_2.tag_name))
        result = await delete_tag(
            photo_id=1,
            tag_id=3,
            user=self.user_moderator,
            db=self.db,
        )
        self.assertFalse(check_tag_in_list_tags(result, self.tag_3.tag_name))

    async def test_delete_tag_fail_wrong_user(self):
        with self.assertRaises(HTTPException) as context:
            await delete_tag(
                photo_id=1,
                tag_id=1,
                user=self.user_2,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            context.exception.detail,
            "Only the photo owner, moderator or admin can delete tags",
        )

    async def test_get_tags_success(self):
        result = await get_tags(
            photo_id=2,
            db=self.db,
        )
        self.assertEqual(result, [self.tag_1, self.tag_5, self.tag_6])

    def test__get_tag_success(self):
        result = _get_tag(tag_id=1, db=self.db)
        self.assertEqual(result, self.tag_1)

    def test__get_tag_fail(self):
        with self.assertRaises(HTTPException) as context:
            _get_tag(tag_id=999, db=self.db)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "Tag not found")

    def test__get_photo_success(self):
        result = _get_photo(photo_id=1, db=self.db)
        self.assertEqual(result, self.photo_1)

    def test__get_photo_fail(self):
        with self.assertRaises(HTTPException) as context:
            _get_photo(photo_id=999, db=self.db)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "Photo not found")
