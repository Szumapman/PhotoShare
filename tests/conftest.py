import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.database.db import get_db
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    postgres_db: str = 'default_db'
    postgres_user: str = 'default_user'
    postgres_password: str = 'default_password'
    postgres_host: str = 'localhost'
    postgres_port: str = '5432'
    sqlalchemy_database_url: str = 'sqlite:///./test.db'
    secret_key: str = 'supersecretkey'
    algorithm: str = 'HS256'
    mail_username: str = 'test@example.com'
    mail_password: str = 'testpassword'
    mail_from: str = 'test@example.com'
    mail_port: int = 587
    mail_server: str = 'smtp.test.com'
    mail_from_name: str = 'Test Server'
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True
    cloudinary_name: str = 'test_cloud'
    cloudinary_api_key: str = 'test_api_key'
    cloudinary_api_secret: str = 'test_api_secret'

    class Config:
        env_file = ".env"


settings = Settings()

# Определяем базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Создаем тестовую базу данных SQLite
engine = create_engine(
    settings.sqlalchemy_database_url, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Создание таблиц в базе данных
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(session):
    app = FastAPI()

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "testuser", "email": "test@example.com", "password": "securepassword"}
