from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ..routes.routes_photo import router as photo_router


app = FastAPI()
app.include_router(photo_router)
client = TestClient(app)


@pytest.fixture
def mock_repos(mocker):
    mock_description_photo = mocker.patch(
        '..repository.repos_photo.description_photo',
        return_value={'id': 1, 'description': 'Updated Description'}
    )
    mock_get_photo_link = mocker.patch(
        '..repository.repos_photo.get_photo_link',
        return_value='/path/to/photo.jpg'
    )
    mock_delete_photo = mocker.patch(
        '..repository.repos_photo.delete_photo',
        return_value=True)
    mock_upload_photo = mocker.patch(
        '..repository.repos_photo.upload_photo',
        return_value={'id': 1, 'file_path': '/path/to/photo.jpg'}
    )
    return mock_description_photo, mock_get_photo_link, mock_delete_photo, mock_upload_photo


@pytest.mark.asyncio
async def test_upload_photo(mock_repos):
    mock_description_photo, mock_get_photo_link, mock_delete_photo, mock_upload_photo = mock_repos
    response = client.post("/photos/", json={"file_path": "/path/to/photo.jpg", "user_id": 1})
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'file_path': '/path/to/photo.jpg'}
    mock_upload_photo.assert_called_once_with({'file_path': '/path/to/photo.jpg', 'user_id': 1})


@pytest.mark.asyncio
async def test_description_photo(mock_repos):
    mock_description_photo, mock_get_photo_link, mock_delete_photo, mock_upload_photo = mock_repos
    response = client.put("/photos/1/description", json={"description": "New Description"})
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'description': 'Updated Description'}
    mock_description_photo.assert_called_once_with(1, 'New Description')


@pytest.mark.asyncio
async def test_download_photo(mock_repos):
    mock_description_photo, mock_get_photo_link, mock_delete_photo, mock_upload_photo = mock_repos
    response = client.get("/photos/1/download")
    assert response.status_code == 200
    mock_get_photo_link.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_photo(mock_repos):
    mock_description_photo, mock_get_photo_link, mock_delete_photo, mock_upload_photo = mock_repos
    response = client.delete("/photos/1?user_id=1")
    assert response.status_code == 200
    mock_delete_photo.assert_called_once_with(1, 1)

