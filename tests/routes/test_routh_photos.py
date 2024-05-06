import pytest

from unittest.mock import patch, MagicMock

from src.database.models import Photo
from src.services.auth import auth_service
from tests.routes.conftest import add_user_to_db, create_x_photos


def test_get_photos(user, session, client):
    new_user = add_user_to_db(user, session)
    no_of_photos = 4
    photos_created = create_x_photos(no_of_photos, session)

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/photos/",
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert len(data) == no_of_photos
        assert data[1]["file_path"] == photos_created[1].file_path
