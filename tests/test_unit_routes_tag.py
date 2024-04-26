import pytest
from fastapi import HTTPException, FastAPI
from src.routes.tag import add_tag_to_photo
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from src.database.models import Photo, Tag
from src.repository import tags

app = FastAPI()


class MockSession:
    def __init__(self, photo=None):
        self.photo = photo

    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.photo

    def commit(self):
        pass


def test_add_tag_to_photo_success(mocker):
    """
    Test if tags can be added to a photo successfully.
    """
    mock_session = MockSession(photo=Photo())
    mocker.patch("src.database.db.get_db", return_value=mock_session)
    mocker.patch(
        "src.repository.tags.get_or_create_tag", return_value=tags.Tag(tag_name="test")
    )
    photo = Photo(id=1, file_path="test.jpg", description="Sample description")
    tag_name = "test"
    add_tag_to_photo(photo.id, tag1=tag_name, db=mock_session)
    assert any(tag.tag_name == tag_name for tag in mock_session.photo.tags)


def test_add_tag_to_photo_photo_not_found():
    """
    Test if HTTPException is raised when photo is not found.
    """
    photo_id = 999
    tags = ["tag1"]
    db_session = MagicMock(spec=Session)
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        add_tag_to_photo(photo_id, *tags, db=db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Photo not found with ID: 999"
    assert len(db_session.commit.call_args_list) == 0


def test_add_tags_to_photo_maximum_tags_reached():
    """
    Test if HTTPException is raised when maximum tags are reached.
    """
    db_mock = MagicMock(spec=Session)
    photo_mock = MagicMock(spec=Photo)
    db_mock.query().filter().first.return_value = photo_mock
    photo_mock.tags = [Tag(tag_name=f"tag{i}") for i in range(5)]
    with pytest.raises(HTTPException) as excinfo:
        add_tag_to_photo(photo_id=1, tag1="tag6", db=db_mock)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Maximum number of tags reached for this photo"


class TestAddTagToPhoto:
    """
    Test class for add_tag_to_photo function.
    """

    def test_add_tags_to_photo_tag_already_exists(self):
        """
        Test if HTTPException is raised when tag already exists for the photo.
        """
        db_mock = MagicMock(spec=Session)
        photo_mock = MagicMock(spec=Photo)
        db_mock.query().filter().first.return_value = photo_mock
        photo_mock.tags = [Tag(tag_name="existing_tag")]
        with pytest.raises(HTTPException) as excinfo:
            add_tag_to_photo(
                photo_id=1,
                tag1="existing_tag",
                db=db_mock,
            )
        assert excinfo.value.status_code == 400
        assert (
            str(excinfo.value.detail)
            == "Tag 'existing_tag' already exists for this photo"
        )
