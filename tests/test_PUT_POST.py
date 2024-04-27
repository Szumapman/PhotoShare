import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from main import app
from src.database.models import Base, Photo
from src.database.db import engine

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def test_db(setup_db):
    _db = Session(bind=engine)
    try:
        yield _db
    finally:
        _db.close()


@pytest.fixture()
def test_photo(test_db):
    photo = Photo(file_path="http://example.com/photo.jpg", description="Original", user_id=1)
    test_db.add(photo)
    test_db.commit()
    return photo


def test_upload_photo_authenticated(test_db):
    with patch('cloudinary.uploader.upload') as mock_upload:
        mock_upload.return_value = {'url': 'http://example.com/test.jpg'}
        photo_data = {
            'file': ('filename.jpg', b'fake image data', 'image/jpeg'),
            'description': 'Test photo upload',
            'tags': 'nature,landscape'
        }
        headers = {"Authorization": "Bearer fake_token"}
        response = client.post(
            "/photos/",
            files=photo_data,
            headers=headers
        )
        assert response.status_code == 200
        assert 'http://example.com/test.jpg' in response.json()['file_path']
        assert 'Test photo upload' == response.json()['description']


def test_upload_photo_unauthenticated():
    with patch('cloudinary.uploader.upload') as mock_upload:
        mock_upload.return_value = {'url': 'http://example.com/test.jpg'}
        photo_data = {
            'file': ('filename.jpg', b'fake image data', 'image/jpeg'),
            'description': 'Test photo upload',
            'tags': 'nature,landscape'
        }
        response = client.post(
            "/photos/",
            files=photo_data
        )
        assert response.status_code == 401


def test_update_photo_description_authenticated(test_photo):
    update_data = {'description': 'Updated description'}
    headers = {"Authorization": "Bearer fake_token"}
    response = client.patch(
        f"/photos/{test_photo.id}/description",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert 'Updated description' == response.json()['new_description']


def test_update_photo_description_unauthenticated(test_photo):
    update_data = {'description': 'Updated description'}
    response = client.patch(
        f"/photos/{test_photo.id}/description",
        json=update_data
    )
    assert response.status_code == 401
