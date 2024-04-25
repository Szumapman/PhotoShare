import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.orm import Session
from src.routes.tag import get_or_create_tag
from src.schemas import TagIn, PhotoIn, UserOut, TagOut
from src.repository import tags


pytestmark = pytest.mark.asyncio


async def test_get_or_create_tag():
    """
    Test the get_or_create_tag function for creating a new tag.

    Checks whether the function correctly creates a new tag based on the provided data,
    and then returns it as the result of the operation.

    Args:
        tag_data (TagIn): Data for the new tag.
        photo_data (PhotoIn): Data for the photo associated with the tag.
        current_user (UserOut): The currently authenticated user.
        db_mock (MagicMock): An object simulating the database session.

    Returns:
        bool: True if the test succeeded.

    """

    tag_data = TagIn(tag_name="test_tag")
    photo_data = PhotoIn(
        file_path="test.jpg",
        description="Test photo",
        filename="test.jpg",
        tags=[{"tag_id": "tag_id", "tag_name": "test_tag"}],
    )
    current_user = UserOut(
        id=1,
        username="test_user",
        email="test@example.com",
        role="standard",
        password="Password!",
    )
    db_mock = MagicMock(Session)
    tags.get_or_create_tag = AsyncMock(return_value=TagOut(id=1, tag_name="test_tag"))
    result = await get_or_create_tag(tag_data, photo_data, current_user, db_mock)
    assert result


async def test_get_or_create_existing_tag():
    """
    Test the get_or_create_tag function for retrieving an existing tag.

    Checks whether the function correctly retrieves an existing tag from the database based on the provided data,
    and then returns it as the result of the operation.

    Args:
        tag_name (str): The name of the existing tag.
        tag_data (TagIn): Data for the existing tag.
        photo_data (PhotoIn): Data for the photo associated with the tag.
        current_user (UserOut): The currently authenticated user.
        db_mock (MagicMock): An object simulating the database session.

    Returns:
        bool: True if the test succeeded.

    """

    tag_name = "existing_tag"
    tag_data = TagIn(tag_name=tag_name)
    photo_data = PhotoIn(
        file_path="test.jpg",
        description="Test photo",
        filename="test.jpg",
        tags=[{"tag_id": "tag_id", "tag_name": tag_name}],
    )
    current_user = UserOut(
        id=1,
        username="test_user",
        email="test@example.com",
        role="standard",
        password="Password!",
    )
    db_mock = MagicMock(Session)
    tags.get_or_create_tag = MagicMock(return_value=TagOut(id=1, tag_name=tag_name))
    result = await get_or_create_tag(tag_data, photo_data, current_user, db_mock)
    assert result == TagOut(id=1, tag_name=tag_name)
