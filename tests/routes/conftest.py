from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image


from main import app
from src.services.auth import auth_service
from src.database.models import Base, User, Photo
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="function")
def user_admin():
    class UserAdmin:
        def __init__(self, username, email, password):
            self.username = username
            self.email = email
            self.password = password
            self.role = "standard"
            self.is_active = True
            self.confirmed = True

        def dict(self):
            return {
                "username": self.username,
                "password": self.password,
                "email": self.email,
                "role": self.role,
                "is_active": self.is_active,
                "confirmed": self.confirmed,
            }

    return UserAdmin(
        username="userAdmin", email="admin@email.com", password="stringQ1!"
    )


TEST_PASSWORD = "stringQ1!"


@pytest.fixture(scope="function")
def user():
    class User:
        def __init__(self, username, email, password):
            self.username = username
            self.email = email
            self.password = auth_service.get_password_hash(password)
            self.role = "standard"
            self.is_active = True
            self.confirmed = True

        def dict(self):
            return {
                "username": self.username,
                "password": self.password,
                "email": self.email,
                "role": self.role,
                "is_active": self.is_active,
                "confirmed": self.confirmed,
            }

    return User(username="userTest", email="test@email.com", password=TEST_PASSWORD)


@pytest.fixture(scope="function")
def user_for_token():
    return {
        "username": "user_token",
        "email": "user_token@example.com",
        "password": TEST_PASSWORD,
    }


@pytest.fixture(scope="module")
def mock_image(width=500, height=500, color=(255, 0, 0)):
    """
    Create a mock picture.

    Args:
    - width (int): Width of the picture.
    - height (int): Height of the picture.
    - color (tuple): RGB color tuple for the picture background.

    Returns:
    - BytesIO: BytesIO object containing the mock picture.
    """

    image = Image.new("RGB", (width, height), color)
    image_bytes_io = BytesIO()
    image.save(image_bytes_io, format="PNG")
    image_bytes_io.seek(0)

    return image_bytes_io


@pytest.fixture
def photo():
    class PhotoTest:
        def __init__(self, id, file_path, qr_path, description, user_id):
            self.id = id
            self.file_path = file_path
            self.qr_path = qr_path
            self.description = description
            self.user_id = user_id

        def dict(self):
            return {
                "id": self.id,
                "file_path": self.file_path,
                "qr_path": self.qr_path,
                "description": self.description,
                "user_id": self.user_id,
            }

    return PhotoTest(
        id=1,
        file_path="photo_url",
        qr_path="qr_path",
        description="description",
        user_id=1,
    )


def add_user_to_db(user: user, db: session):
    new_user = User(
        username=user.username,
        email=user.email,
        password=user.password,
        role=user.role,
        is_active=user.is_active,
        confirmed=user.confirmed,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def add_not_confirmed_user_to_db(user: user, db: session):
    new_user = add_user_to_db(user=user, db=db)
    new_user.confirmed = False
    db.commit()
    db.refresh(new_user)
    return new_user


def add_user_with_token(user: user, db: session):
    new_user = add_user_to_db(user=user, db=db)
    new_user.refresh_token = "<REFRESH TOKEN>"
    db.commit()
    db.refresh(new_user)
    return new_user


def create_x_photos(no_of_photos: int, db: session):
    photos = []
    for i in range(no_of_photos):
        photo = Photo(
            file_path="photo_url",
            qr_path="qr_path",
            description="description",
            user_id=1,
        )
        db.add(photo)
        db.commit()
        photos.append(photo)
    return photos
