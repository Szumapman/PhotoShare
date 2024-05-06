import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.services.auth import auth_service
from src.database.models import Base, User
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


# async def add_user_to_db_with_tokens(user: user, db: session):
#     new_user = add_user_to_db(user=user, db=db)
#     access_token = await auth_service.create_access_token(data={"sub": new_user.email})
#     new_user.refresh_token = await auth_service.create_refresh_token(
#         data={"sub": new_user.email}
#     )
#     db.commit()
#     db.refresh(new_user)
#     return new_user
