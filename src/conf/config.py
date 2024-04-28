from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    Attributes:
        postgres_db (str): PostgreSQL database name.
        postgres_user (str): PostgreSQL username.
        postgres_password (str): PostgreSQL password.
        postgres_host (str, optional): PostgreSQL host (default is "localhost").
        postgres_port (int): PostgreSQL port.
        sqlalchemy_database_url (str): SQLAlchemy database URL.
        secret_key (str): Secret key for cryptographic operations.
        algorithm (str): Algorithm for token generation (e.g., "HS256").
        mail_username (str): SMTP username for sending emails.
        mail_password (str): SMTP password for sending emails.
        mail_from (str): Email address to use as the "From" address.
        mail_port (int): SMTP port for email communication.
        mail_server (str): SMTP server hostname.
        mail_from_name (str): Display name for the "From" email address.
        mail_starttls (bool): Enable STARTTLS for secure email communication.
        mail_ssl_tls (bool): Enable SSL/TLS for secure email communication.
        use_credentials (bool): Flag indicating whether to use credentials for email.
        validate_certs (bool): Flag indicating whether to validate SSL certificates.
        redis_host (str, optional): Redis server hostname (default is "localhost").
        redis_port (int, optional): Redis server port (default is 6379).
        redis_password (str): Redis server password (default is "password").
        cloudinary_name (str): Cloudinary account name.
        cloudinary_api_key (str): Cloudinary API key.
        cloudinary_api_secret (str): Cloudinary API secret.

    Config:
        env_file (str): Path to the environment file (default is ".env").
        env_file_encoding (str): Encoding of the environment file (default is "utf-8").
    """

    postgres_db: str = 'default_db'
    postgres_user: str = 'default_user'
    postgres_password: str = 'default_password'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    sqlalchemy_database_url: str = 'sqlite:///./test.db'
    secret_key: str = 'your_secret_key'
    algorithm: str = 'HS256'
    mail_username: str = 'your_email@example.com'
    mail_password: str = 'your_email_password'
    mail_from: str = 'your_email@example.com'
    mail_port: int = 587
    mail_server: str = 'smtp.example.com'
    mail_from_name: str = 'Example Name'
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str = 'password'
    cloudinary_name: str = 'your_cloudinary_name'
    cloudinary_api_key: str = 'your_cloudinary_api_key'
    cloudinary_api_secret: str = 'your_cloudinary_api_secret'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
