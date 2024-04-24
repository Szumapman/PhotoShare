import pickle
from typing import Optional
from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from redis import Redis
import bcrypt

from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas import UserOut


class Auth:
    """
    Utility class for handling authentication-related operations.

    Attributes:
        SECRET_KEY (str): Secret key used for JWT token generation.
        ALGORITHM (str): Algorithm used for JWT token generation.
        oauth2_scheme (OAuth2PasswordBearer): OAuth2 password bearer scheme.
        r (Redis): Redis client for caching.

    Methods:
        verify_password(plain_password, hashed_password): Verify if the plain password matches the hashed password.
        get_password_hash(password): Hash the provided password.
        create_access_token(data, expires_delta): Generate an access token for the provided data.
        create_refresh_token(data, expires_delta): Generate a refresh token for the provided data.
        decode_refresh_token(refresh_token): Decode the provided refresh token and return the associated email.
        get_current_user(token, db): Get the currently authenticated user based on the provided access token.
        create_email_token(data): Generate a token for email verification.
        get_email_from_token(token): Decode the provided token and return the associated email.

    """

    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        # password=settings.redis_password,
        db=0,
    )

    def verify_password(self, plain_password, hashed_password):
        """Verify if the plain password matches the hashed password."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def get_password_hash(self, password: str):
        """Hash the provided password."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """Generate an access token for the provided data."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """Generate a refresh token for the provided data."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """Decode the provided refresh token and return the associated email."""
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ) -> UserOut:
        """Get the currently authenticated user based on the provided access token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            await self.r.set(f"user:{email}", pickle.dumps(user))
            await self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """Generate a token for email verification."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """Decode the provided token and return the associated email."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
