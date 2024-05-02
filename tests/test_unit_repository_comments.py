import unittest

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.repository.comments import add_comment, update_comment, delete_comment
from src.database.models import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestComments(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()
        self.comment_id = 1
        self.wrong_comment_id = 999
        self.user_id = 1
        self.photo_id = 1
        self.text = "Test comment"

    def tearDown(self):
        self.db.close()

    async def test_add_comment(self):
        result = await add_comment(
            self.user_id,
            self.photo_id,
            self.text,
            db=self.db,
        )
        self.assertEqual(result.id, self.comment_id)
        self.assertEqual(result.text, self.text)
        self.assertEqual(result.user_id, self.user_id)
        self.assertEqual(result.photo_id, self.photo_id)

    async def test_update_comment_success(self):
        # prepare comment in db to test
        await add_comment(self.user_id, self.photo_id, self.text, db=self.db)

        result = await update_comment(
            comment_id=self.comment_id,
            user_id=self.user_id,
            text="Update comment",
            db=self.db,
        )
        self.assertEqual(result.id, self.comment_id)
        self.assertEqual(result.text, "Update comment")
        self.assertEqual(result.user_id, self.user_id)
        self.assertEqual(result.photo_id, self.photo_id)

    async def test_update_comment_by_another_user(self):
        await add_comment(self.user_id, self.photo_id, self.text, db=self.db)

        with self.assertRaises(HTTPException) as context:
            await update_comment(
                comment_id=self.comment_id,
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
                self.user_id,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_delete_comment_success(self):
        await add_comment(self.user_id, self.photo_id, self.text, db=self.db)

        result = await delete_comment(self.comment_id, db=self.db)
        self.assertEqual(result.id, self.comment_id)

    async def test_delete_comment_no_exist_comment(self):
        with self.assertRaises(HTTPException) as context:
            await update_comment(
                self.wrong_comment_id,
                self.text,
                self.user_id,
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
