import pytest
from fastapi import HTTPException
from src.routes.tag import add_tag_to_photo
from sqlalchemy.orm import Session
from unittest.mock import MagicMock


def test_add_tag_to_poto_photo_not_found():
    photo_id = 999
    tags = ["tag1"]
    db_session = MagicMock(spec=Session)
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        add_tag_to_photo(photo_id, *tags, db=db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Photo not found with ID: 999"
    assert len(db_session.commit.call_args_list) == 0
