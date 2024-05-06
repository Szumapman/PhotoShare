import unittest

from fastapi import HTTPException, status

from src.repository.comments import add_comment, update_comment, delete_comment
from src.database.models import Base, User, Photo, PhotoTag, Comment, Tag
from tests.repository.db_test_config import engine, testing_session_local


class TestComments(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = testing_session_local()
        self.comment_id = 1
        self.wrong_comment_id = 999
        self.user_id = 1
        self.photo_id = 1
        self.text = "Test comment"
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
        self.db.refresh(self.user)
        self.db.refresh(self.user_2)
        self.db.refresh(self.photo_1)
        self.db.refresh(self.photo_2)
        self.comment_1 = Comment(
            text="test_comment_1", user_id=self.user.id, photo_id=self.photo_1.id
        )
        self.comment_2 = Comment(
            text="test_comment_2", user_id=self.user_2.id, photo_id=self.photo_1.id
        )
        self.comment_3 = Comment(
            text="test_comment_3", user_id=self.user.id, photo_id=self.photo_1.id
        )
        self.comment_4 = Comment(
            text="test_comment_4", user_id=self.user_2.id, photo_id=self.photo_2.id
        )
        self.db.add(self.comment_1)
        self.db.add(self.comment_2)
        self.db.add(self.comment_3)
        self.db.add(self.comment_4)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    async def test_add_comment(self):
        result = await add_comment(
            self.user_moderator.id,
            self.photo_1.id,
            self.text,
            db=self.db,
        )
        self.assertEqual(result.id, 5)
        self.assertEqual(result.text, self.text)
        self.assertEqual(result.user_id, self.user_moderator.id)
        self.assertEqual(result.photo_id, self.photo_id)

    async def test_update_comment_success(self):
        result = await update_comment(
            comment_id=self.comment_1.id,
            user_id=self.user.id,
            text="Update comment",
            db=self.db,
        )
        self.assertEqual(result.id, self.comment_1.id)
        self.assertEqual(result.text, "Update comment")
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.photo_id, self.photo_1.id)

    async def test_update_comment_by_another_user(self):
        with self.assertRaises(HTTPException) as context:
            await update_comment(
                comment_id=self.comment_1.id,
                text="Update comment",
                user_id=999,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)

    async def test_update_no_exist_comment(self):
        with self.assertRaises(HTTPException) as context:
            await update_comment(
                self.wrong_comment_id,
                self.text,
                self.user.id,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_delete_comment_success(self):
        result = await delete_comment(self.comment_1.id, db=self.db)
        self.assertEqual(result.id, self.comment_1.id)
        result = self.db.query(Comment).filter_by(id=self.comment_1.id).first()
        self.assertIsNone(result)

    async def test_delete_comment_no_exist_comment(self):
        with self.assertRaises(HTTPException) as context:
            await update_comment(
                self.wrong_comment_id,
                self.text,
                self.user_id,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
