import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database.models import Base, User, Photo, Comment, Tag, PhotoTag


@pytest.fixture(scope='module')
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def user(session):
    email = "john@example.com"
    new_user = User(
        name_to_show="JohnDoe",
        first_name="John",
        last_name="Doe",
        birth_date=datetime(1990, 1, 1),
        email=email,
        verified=True,
    )
    session.add(new_user)
    session.commit()
    yield new_user
    session.delete(new_user)
    session.commit()


@pytest.fixture
def photo(user, session):
    new_photo = Photo(file_path="/path/to/photo.jpg", user=user)
    session.add(new_photo)
    session.commit()
    return new_photo


@pytest.fixture
def comment(user, photo, session):
    new_comment = Comment(text="Nice photo!", user=user, photo=photo)
    session.add(new_comment)
    session.commit()
    return new_comment


@pytest.fixture
def tag(photo, session):
    new_tag = Tag(tag_name="Nature", user_id=photo.user_id)
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)
    return new_tag


@pytest.fixture
def tags(photo, session):
    new_tags = []
    tag_names = ["Nature", "Travel", "Food"]
    for tag_name in tag_names:
        new_tag = Tag(tag_name=tag_name, user_id=photo.user_id)
        session.add(new_tag)
        session.commit()
        session.refresh(new_tag)
        new_tags.append(new_tag)
    return new_tags


def test_create_user(user):
    assert user.user_id is not None


def test_add_photo_to_user(photo):
    assert photo.photo_id is not None
    assert photo.user.name_to_show == "JohnDoe"


def test_add_comment_to_photo(comment):
    assert comment.comment_id is not None
    assert comment.user.name_to_show == "JohnDoe"
    assert comment.photo.file_path == "/path/to/photo.jpg"


def test_add_tag_to_photo(session, tag, tags):
    # Create a new photo
    new_photo = Photo(file_path="/path/to/photo.jpg")
    session.add(new_photo)
    session.commit()

    # Add the initial tag to the photo
    tag.photos.append(new_photo)
    session.commit()

    # Add tags to the photo only if they are not already associated with the photo
    for t in tags:
        if t not in new_photo.tags:
            t.photos.append(new_photo)
    session.commit()

    # Checking that both tags are actually added to the photo
    assert tag in new_photo.tags
    for t in tags:
        assert t in new_photo.tags


def test_delete_comment(comment, session):
    session.delete(comment)
    session.commit()
    assert session.query(Comment).filter_by(comment_id=comment.comment_id).first() is None


def test_delete_photo(photo, session):
    session.delete(photo)
    session.commit()
    assert session.query(Photo).filter_by(photo_id=photo.photo_id).first() is None


def test_delete_tag(tag, session):
    session.delete(tag)
    session.commit()
    assert session.query(Tag).filter_by(tag_id=tag.tag_id).first() is None


if __name__ == "__main__":
    pytest.main()
