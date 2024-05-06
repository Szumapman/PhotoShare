from unittest.mock import MagicMock, AsyncMock

from src.database.models import User
from src.services.auth import auth_service
from tests.routes.conftest import (
    TEST_PASSWORD,
    add_user_to_db,
    add_not_confirmed_user_to_db,
)


def test_create_user(client, user_admin, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user_admin.dict(),
    )
    assert response.status_code == 201, response.text
    data = response.json()
    print(data)
    assert data["email"] == user_admin.email
    assert "id" in data


def test_repeat_create_user(user_admin, session, client):
    add_user_to_db(user_admin, session)
    response = client.post("/api/auth/signup", json=user_admin.dict())
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_wrong_email(user, session, client):
    add_user_to_db(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": "email", "password": user.password},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_login_user_not_confirmed(user, session, client):
    add_not_confirmed_user_to_db(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": user.password},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_wrong_password(user, session, client):
    add_user_to_db(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": "password"},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_user_success(user, session, client):
    add_user_to_db(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": TEST_PASSWORD},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid_user(user, session, client, monkeypatch):
    add_user_to_db(user, session)

    async def mock_decode_refresh_token(token):
        return user.email

    monkeypatch.setattr(
        auth_service,
        "decode_refresh_token",
        AsyncMock(side_effect=mock_decode_refresh_token),
    )
    response = client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": f"Bearer invalid_refresh_token"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid refresh token"
