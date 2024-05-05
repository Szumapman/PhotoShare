import pytest
from src.database.models import User
from src.services.auth import auth_service
import pytest_asyncio


@pytest_asyncio.fixture()
async def get_token(user):
    token = await auth_service.create_access_token(data={"sub": user["email"]})
    return token

def test_get_user_profile_nonexistent_user(client):
    response = client.get("/100")
    assert response.status_code == 404, response.text

@pytest.mark.asyncio
async def test_get_current_user(client, user, session, get_token):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.get(
        "api/users/me",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
