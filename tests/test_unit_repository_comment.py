from datetime import datetime
from unittest import TestCase, mock
from unittest.mock import AsyncMock, MagicMock, patch
from src.database.models import Comment
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.database.models import Comment
from src.repository.comment import add_comment, update_comment
import asyncio


class TestAddComment(TestCase):

    def test_add_comment_empty_text(self):
        user_id = 1
        photo_id = 1
        text = ""
        mock_session = MagicMock()

        fixed_date = datetime(2024, 4, 28, 12, 0, 0)
        with patch("src.repository.comment.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_date
            try:
                new_comment = add_comment(user_id, photo_id, text)
                assert False, "Expected HTTPException was not raised"
            except HTTPException as e:
                assert e.status_code == 422

    def test_add_comment_invalid_user_id(self):
        fake_session = mock.Mock(spec=Session)
        with self.assertRaises(ValueError) as context:
            asyncio.run(add_comment(user_id=0, photo_id=1, text="Test comment"))
        self.assertEqual(str(context.exception), "Invalid user_id")

    def test_add_comment_invalid_photo_id(self):
        fake_session = mock.Mock(spec=Session)
        with self.assertRaises(ValueError) as context:
            asyncio.run(add_comment(user_id=1, photo_id=0, text="Test comment"))
        self.assertEqual(str(context.exception), "Invalid photo_id")

    ######################
    @mock.patch("src.repository.comment.datetime")
    async def test_add_comment(self, mock_datetime):
        mock_now = datetime(2024, 4, 28, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        expected_comment = Comment(
            user_id=1, photo_id=1, text="Test comment", created_at=mock_now
        )
        actual_comment = await add_comment(user_id=1, photo_id=1, text="Test comment")
        self.assertEqual(actual_comment.user_id, expected_comment.user_id)
        self.assertEqual(actual_comment.photo_id, expected_comment.photo_id)
        self.assertEqual(actual_comment.text, expected_comment.text)
        self.assertEqual(actual_comment.created_at, expected_comment.created_at)

    @mock.patch("src.repository.comment.datetime")
    def test_update_comment(self, mock_datetime):
        mock_now = datetime(2024, 4, 28, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        initial_text = "Initial comment text"
        updated_text = "Updated comment text"
        comment_id = 1
        fake_session = mock.Mock(spec=Session)
        fake_comment = Comment(
            id=comment_id,
            user_id=1,
            photo_id=1,
            text=initial_text,
            date_posted=mock_now,
        )
        fake_session.query().filter().first.return_value = fake_comment
        updated_comment = asyncio.run(
            update_comment(comment_id, updated_text, fake_session)
        )
        self.assertEqual(updated_comment.text, updated_text)

    def test_update_non_existing_comment(self):
        fake_session = mock.Mock(spec=Session)
        fake_session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            asyncio.run(update_comment(9999, "Some text", fake_session))
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Comment not found")

    def test_update_comment_empty_text(self):
        fake_session = mock.Mock(spec=Session)
        fake_session.query().filter().first.return_value = None

        async def run_update_comment():
            with self.assertRaises(HTTPException) as context:
                await update_comment(comment_id=1, text="", db=fake_session)
            return context.exception

        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(run_update_comment())
        loop.close()
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.detail, "Comment not found")
