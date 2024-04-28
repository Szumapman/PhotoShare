import pytest
from sqlalchemy.orm import Session

from main import app
from src.database.models import Comment
from src.schemas import CommentIn, CommentOut, UserRoleValid, UserOut
from fastapi import HTTPException
from src.services.auth import Auth
from src.database.db import get_db
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Depends
from fastapi.testclient import TestClient
from src.routes.comments import router, create_comment


client = TestClient(app)


def test_update_comment():
    with patch(
        "src.services.auth.auth_service.get_current_user"
    ) as mock_get_current_user, patch.object(Session, "commit") as mock_commit, patch(
        "src.database.models.Comment"
    ) as mock_comment_model:
        mock_get_current_user.return_value = MagicMock(id=1)
        mock_comment = MagicMock(spec=Comment)
        mock_comment.id = 1
        mock_comment.user_id = 1
        mock_comment_model.query.return_value.filter.return_value.first.return_value = (
            mock_comment
        )
        response = client.put("/comments/1/", json={"text": "Updated comment"})
        assert response.status_code == 200
        assert response.json() == {
            "photo_id": 1,
            "user_id": 1,
            "text": "Updated comment",
        }
        mock_commit.assert_called_once()


def test_delete_comment():
    with patch("src.routes.comments.get_db"), patch(
        "src.routes.comments.auth_service"
    ) as mock_auth_service:
        mock_auth_service.get_current_user.return_value = MagicMock(
            id=1, role=UserRoleValid.admin
        )
        with patch.object(Session, "commit") as mock_commit:
            response = client.delete("/comments/1/")
            assert response.status_code == 200
            assert response.json() == {"message": "Comment deleted successfully"}
            mock_commit.assert_called_once()


def test_create_comment_unauthorized():
    with patch("src.routes.comments.get_db"), patch(
        "src.routes.comments.auth_service"
    ) as mock_auth_service:
        mock_auth_service.get_current_user.return_value = None
        response = client.post(
            "/comments/photos/1/comments/", json={"photo_id": 1, "text": "Test comment"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}


def test_update_comment_not_owner():
    with patch("src.routes.comments.get_db"), patch(
        "src.routes.comments.auth_service"
    ) as mock_auth_service:
        mock_auth_service.get_current_user.return_value = MagicMock(id=2)
        response = client.put("/comments/1/", json={"text": "Updated comment"})
        assert response.status_code == 403
        assert response.json() == {
            "detail": "Forbidden: You can only edit your own comments"
        }


def test_delete_comment_unauthorized():
    with patch("src.routes.comments.auth_service") as mock_auth_service:
        mock_user = MagicMock(id=1000, role=UserRoleValid.standard)
        mock_auth_service.get_current_user.return_value = mock_user
        response = client.delete("/comments/1000/")
        assert response.status_code == 403


def test_delete_comment_not_found():
    with patch("src.routes.comments.get_db"), patch(
        "src.routes.comments.auth_service"
    ) as mock_auth_service:
        mock_auth_service.get_current_user.return_value = MagicMock(
            id=1, role=UserRoleValid.admin
        )
        with patch.object(Session, "delete") as mock_delete:
            mock_delete.side_effect = lambda _: None
            response = client.delete("/comments/1/")
            assert response.status_code == 404
            assert response.json() == {"detail": "Comment not found"}


#######################
def test_create_comment_standard_user():
    auth_service = Auth()
    comment_data = CommentIn(photo_id=1, text="Test comment")
    mock_auth_service = MagicMock()
    mock_auth_service.get_current_user.return_value = UserOut(
        id=1,
        username="example_user",
        email="user@example.com",
        password="example_password",
        role=UserRoleValid.standard,
    )
    mock_db = MagicMock()
    try:
        response = create_comment(
            comment_data=comment_data, current_user="token", db=mock_db
        )
        assert response is not None
    except HTTPException as e:
        assert e.status_code == 401


def test_create_comment_moderator():
    auth_service = Auth()
    comment_data = CommentIn(photo_id=1, text="Test comment")
    mock_auth_service = MagicMock()
    mock_auth_service.get_current_user.return_value = UserOut(
        id=1,
        username="example_user",
        email="user@example.com",
        password="example_password",
        role=UserRoleValid.moderator,
    )
    mock_db = MagicMock()
    try:
        response = create_comment(
            comment_data=comment_data, current_user="token", db=mock_db
        )
        assert response is not None
    except HTTPException as e:
        assert e.status_code == 401


def test_create_comment_admin():
    auth_service = Auth()
    comment_data = CommentIn(photo_id=1, text="Test comment")
    mock_auth_service = MagicMock()
    mock_auth_service.get_current_user.return_value = UserOut(
        id=1,
        username="example_user",
        email="user@example.com",
        password="example_password",
        role=UserRoleValid.admin,
    )
    mock_db = MagicMock()
    try:
        response = create_comment(
            comment_data=comment_data, current_user="token", db=mock_db
        )
        assert response is not None
    except HTTPException as e:
        assert e.status_code == 401
