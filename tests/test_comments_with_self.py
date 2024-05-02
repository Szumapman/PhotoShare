import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status

from src.database.models import Comment
from src.repository.comments import add_comment, update_comment, delete_comment

mock_db = MagicMock()
mock_db.commit = AsyncMock()
mock_db.add = MagicMock(return_value=None)
mock_db.refresh = MagicMock(return_value=None)

@patch("src.database.models.Comment")
@patch("src.database.db.get_db")
class TestComments(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.add = MagicMock(return_value=None)
        self.mock_db.refresh = MagicMock(return_value=None)

    async def test_add_comment_success(self):
        user_id = 1
        photo_id = 1
        text = "Test comment"
        new_comment = Comment(id=1, user_id=user_id, photo_id=photo_id, text=text)
        result = await add_comment(user_id, photo_id, text, self.mock_db)

        self.assertIsNotNone(result, new_comment)
        self.assertEqual(result.id, new_comment.id)
        self.assertEqual(result.text, new_comment.text)
        self.assertEqual(result.user_id, new_comment.user_id)
        self.assertEqual(result.photo_id, new_comment.photo_id)


    async def test_add_comment_invalid_text(self):
        user_id = 1
        photo_id = 1
        text = None

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(ValueError):
            await add_comment(user_id, photo_id, text, self.mock_db)


    async def test_add_comment_nonexistent_photo(self):
        user_id = 1
        photo_id = 999
        text = "Test comment"

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            add_comment(user_id, photo_id, text, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Photo with id 999 does not exist."


    async def test_add_comment_unauthenticated_user(self):
        user_id = None
        photo_id = 1
        text = "Test comment"

        with pytest.raises(HTTPException) as excinfo:
            add_comment(user_id, photo_id, text, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


    async def test_update_comment_success(self, mock_comment):
        comment_id = 1
        text = "Updated comment"
        user_id = 1
        mock_comment.return_value = Comment(
            id=comment_id, user_id=user_id, photo_id=1, text=text
        )
        self.mock_db.query().filter().first.return_value = mock_comment
        result = await update_comment(comment_id, text, user_id, self.mock_db)
        self.assertIsNotNone(result)
        self.assertEqual(result.text, text)


    async def test_update_comment_invalid_text(self):
        comment_id = 1
        text = ""
        user_id = 1

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            update_comment(comment_id, text, user_id, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


    async def test_update_comment_unauthenticated_user(self):
        comment_id= 1
        text= "Updated comment"
        user_id= None

        self.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            update_comment(comment_id, text, user_id, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


    async def test_update_comment_other_user_comment(self):
        logged_in_user_id = 1
        other_user_comment = MagicMock()
        other_user_comment.user_id = 2

        comment_id = 1
        text = "Updated comment"
        user_id = logged_in_user_id

        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            other_user_comment
        )
        with pytest.raises(HTTPException) as excinfo:
            update_comment(comment_id, text, user_id, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
        assert excinfo.value.detail == "Only the owner can update the comment"


    async def test_update_nonexistent_comment(self):
        comment_id = 999
        text = "Updated comment"
        user_id = 1

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            update_comment(comment_id, text, user_id, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Comment not found"


    async def test_delete_comment(self, mock_db, mock_comment):
        comment_id = 1
        mock_comment_instance = mock_comment(
            id=comment_id, user_id=1, photo_id=1, text="Test comment"
        )
        self.mock_db.query().filter().first.return_value = mock_comment_instance
        result = await delete_comment(comment_id, self.mock_db)
        self.assertEqual(result.id, comment_id)
        self.assertEqual(result.text, mock_comment_instance.text)
        self.assertEqual(result.user_id, mock_comment_instance.user_id)
        self.assertEqual(result.photo_id, mock_comment_instance.photo_id)


    async def test_delete_comment_nonexistent_comment(self):
        comment_id = 1

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            update_comment(comment_id, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Comment not found"


    async def test_delete_comment_standard_user(self):
        user_id = 1
        comment_id = 1

        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            delete_comment(comment_id, db=self.mock_db)
        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
