import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Comment
from src.repository.comments import add_comment, update_comment, delete_comment
from src.schemas import CommentOut, UserOut


class TestComments(unittest.TestCase):
    @patch("src.database.models.Comment")
    @patch("src.database.db.get_db")
    async def test_add_comment_success(self, mock_db):
        user_id = 1
        photo_id = 1
        text = "Test comment"
        new_comment = Comment(id=1, user_id=user_id, photo_id=photo_id, text=text)
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock(return_value=None)
        mock_db.refresh = MagicMock(return_value=None)

        result = await add_comment(user_id, photo_id, text, mock_db)

        self.assertIsNotNone(result, new_comment)
        self.assertEqual(result.id, new_comment.id)
        self.assertEqual(result.text, new_comment.text)
        self.assertEqual(result.user_id, new_comment.user_id)
        self.assertEqual(result.photo_id, new_comment.photo_id)

    @patch("src.database.models.Comment")
    @patch("src.database.db.get_db")
    async def test_add_comment_invalid_text(self, mock_db):
        user_id = 1
        photo_id = 1
        text = None
        with self.assertRaises(ValueError):
            await add_comment(user_id, photo_id, text, mock_db)

    @patch("src.database.models.Comment")
    @patch("src.database.db.get_db")
    async def test_update_comment_success(self, mock_db, mock_comment):
        comment_id = 1
        text = "Updated comment"
        user_id = 1
        mock_comment.return_value = Comment(
            id=comment_id, user_id=user_id, photo_id=1, text=text
        )
        mock_db.query().filter().first.return_value = mock_comment
        # mock_db.commit = MagicMock()
        # mock_db.refresh = MagicMock()

        result = await update_comment(comment_id, text, user_id, mock_db)

        self.assertIsNotNone(result)
        self.assertEqual(result.text, text)

    @patch("src.database.models.Comment")
    @patch("src.database.db.get_db")
    async def test_delete_comment(self, mock_db, mock_comment):
        comment_id = 1
        mock_comment_instance = mock_comment(
            id=comment_id, user_id=1, photo_id=1, text="Test comment"
        )
        mock_db.query().filter().first.return_value = mock_comment_instance
        # mock_db.commit = MagicMock()

        result = await delete_comment(comment_id, mock_db)

        self.assertEqual(result.id, comment_id)
        self.assertEqual(result.text, mock_comment_instance.text)
        self.assertEqual(result.user_id, mock_comment_instance.user_id)
        self.assertEqual(result.photo_id, mock_comment_instance.photo_id)

    @patch("src.database.models.Comment")
    @patch("src.database.db.get_db")
    async def test_delete_comment_already_deleted(self, mock_db):
        comment_id = 1
        mock_db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as cm:
            await delete_comment(comment_id, mock_db)
        self.assertEqual(cm.exception.status_code, status.HTTP_404_NOT_FOUND)

    @patch("src.database.models.Comment")
    @patch("src.database.db.get_db")
    async def test_delete_comment_not_owner(self, mock_db, mock_comment):
        comment_id = 1
        mock_comment_instance = mock_comment(
            id=comment_id, user_id=999, photo_id=1, text="Test comment"
        )  # nie bardzo łapię skąd wiemy, że nie jest właścicielem
        mock_db.query().filter().first.return_value = mock_comment_instance
        with self.assertRaises(HTTPException) as cm:
            await delete_comment(comment_id, mock_db)
        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
