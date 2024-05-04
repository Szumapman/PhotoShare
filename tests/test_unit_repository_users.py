import unittest
from unittest.mock import MagicMock

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Photo, User
from src.schemas import UserIn
from src.repository import users as users_repository
from src.services.auth import auth_service


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username="user1",
            email="test@email.com",
            password="testPass1!",
            role="standard",
            avatar="https://www.gravatar.com/avatar/f2c97b1f2d2898cd2d6466ce95d4ba33",
        )
        self.user_2 = User(
            id=2,
            username="user2",
            email="test2@email.com",
            password="testPass2!",
            role="standard",
            avatar="https://www.gravatar.com/avatar/f2c97b1f2d2898cd2d6466ce95d4ba33",
        )

    async def test_update_current_user_profile_email_exists(self):
        new_user_data = UserIn(
            username="user2",
            email="test2@email.com",
            password="testPass2!",
        )

        self.session.query().filter().first.return_value = self.user_2

        with self.assertRaises(HTTPException) as context:
            await users_repository.update_current_user_profile(
                self.user, new_user_data, self.session
            )
        self.assertEqual(context.exception.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            str(context.exception.detail),
            f"Account with {new_user_data.email} already exists.",
        )

    async def test_update_current_user_profile_user_not_found(self):
        new_user_data = UserIn(
            username="user2",
            email="test@email.com",
            password="testPass2!",
        )

        self.session.query().filter().first.return_value = None

        with self.assertRaises(HTTPException) as context:
            await users_repository.update_current_user_profile(
                self.user, new_user_data, self.session
            )
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            str(context.exception.detail),
            f"User with id: {self.user.id} not found",
        )

    async def test_update_current_user_profile_success(self):
        self.session.query().filter().first.return_value = self.user

        new_user_data = UserIn(
            username="user3",
            email="test3@email.com",
            password="testPass3!",
        )

        updated_user = await users_repository.update_current_user_profile(
            self.user, new_user_data, self.session
        )

        self.assertEqual(updated_user.username, new_user_data.username)
        self.assertEqual(updated_user.email, new_user_data.email)

        updated_user_password = updated_user.password
        updated_password_correct = auth_service.verify_password(
            new_user_data.password, updated_user_password
        )
        self.assertTrue(updated_password_correct)

    async def test_get_user_public_profile_success(self):
        photos = [Photo(id=1, user_id=1), Photo(id=2, user_id=1)]

        user_with_photo_count = (
            self.user.id,
            self.user.username,
            self.user.avatar,
            len(photos),
        )
        self.session.query(User.id, User.username, User.avatar).filter(
            User.id == 1
        ).outerjoin(Photo, User.id == Photo.user_id).add_column(
            func.count(Photo.id).label("photo_count")
        ).group_by(
            User.id
        ).first.return_value = user_with_photo_count

        result = await users_repository.get_user_public_profile(1, self.session)

        self.assertEqual(result.id, self.user.id)
        self.assertEqual(result.username, self.user.username)
        self.assertEqual(result.avatar, self.user.avatar)
        self.assertEqual(result.photo_count, len(photos))

    async def test_get_user_public_profile_id_not_found(self):
        user_with_photo_count = None
        self.session.query(User.id, User.username, User.avatar).filter(
            User.id == 1
        ).outerjoin(Photo, User.id == Photo.user_id).add_column(
            func.count(Photo.id).label("photo_count")
        ).group_by(
            User.id
        ).first.return_value = user_with_photo_count

        with self.assertRaises(HTTPException) as context:
            await users_repository.get_user_public_profile(1, self.session)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            str(context.exception.detail),
            f"User with id: 1 not found",
        )
