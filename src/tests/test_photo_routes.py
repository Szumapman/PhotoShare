import unittest
from unittest.mock import MagicMock, patch
from ..repository import repos_photo


class TestPhotoRoutes(unittest.TestCase):
    def setUp(self):
        self.db_session_mock = MagicMock()

        @patch('..repository.repos_photo.upload_photo')
        def test_upload_photo(self, mock_upload_photo):
            photo_data_mock = MagicMock(user_id=1)
            mock_upload_photo.return_value = {'id': 1, 'file_path': '/path/to/photo.jpg'}
            response = repos_photo.upload_photo(self.db_session_mock, photo_data_mock, user=MagicMock(user_id=1))
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['file_path'], '/path/to/photo.jpg')
            mock_upload_photo.assert_called_once_with(self.db_session_mock, photo_data_mock, user=MagicMock(user_id=1))

        @patch('..repository.repos_photo.description_photo')
        def test_description_photo(self, mock_description_photo):
            mock_description_photo.return_value = {'id': 1, 'description': 'Updated Description'}
            user_mock = MagicMock(user_id=1)
            response = repos_photo.description_photo(self.db_session_mock, 1, 'Updated Description', user=user_mock)
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['description'], 'Updated Description')
            mock_description_photo.assert_called_once_with(self.db_session_mock, 1, 'Updated Description',
                                                           user=user_mock)

        @patch('..repository.repos_photo.get_photo_link')
        def test_download_photo(self, mock_get_photo_link):
            mock_get_photo_link.return_value = '/path/to/photo.jpg'
            response = repos_photo.get_photo_link(self.db_session_mock, 1)
            self.assertEqual(response, '/path/to/photo.jpg')
            mock_get_photo_link.assert_called_once_with(self.db_session_mock, 1)

        @patch('..repository.repos_photo.delete_photo')
        def test_delete_photo(self, mock_delete_photo):
            mock_delete_photo.return_value = True
            user_mock = MagicMock(user_id=1)
            response = repos_photo.delete_photo(self.db_session_mock, 1, user=user_mock)
            self.assertTrue(response)
            mock_delete_photo.assert_called_once_with(self.db_session_mock, 1, user=user_mock)

    if __name__ == '__main__':
        unittest.main()
