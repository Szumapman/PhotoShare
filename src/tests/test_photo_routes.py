import unittest
from unittest.mock import MagicMock

from ..repository.repos_photo import upload_photo, description_photo, get_photo_link, delete_photo


class TestPhotoRoutes(unittest.TestCase):
    def setUp(self):
        self.mock_upload_photo = MagicMock()
        self.mock_description_photo = MagicMock()
        self.mock_get_photo_link = MagicMock()
        self.mock_delete_photo = MagicMock()

    def test_upload_photo(self):
        self.mock_upload_photo.return_value = {'id': 1, 'file_path': '/path/to/photo.jpg'}
        response = upload_photo('/path/to/photo.jpg')
        self.assertEqual(response['id'], 1)
        self.assertEqual(response['file_path'], '/path/to/photo.jpg')

    def test_description_photo(self):
        self.mock_description_photo.return_value = {'id': 1, 'description': 'Updated Description'}
        response = description_photo(1, 'New Description')
        self.assertEqual(response['id'], 1)
        self.assertEqual(response['description'], 'Updated Description')

    def test_download_photo(self):
        self.mock_get_photo_link.return_value = '/path/to/photo.jpg'
        response = get_photo_link(1)
        self.assertEqual(response, '/path/to/photo.jpg')

    def test_delete_photo(self):
        self.mock_delete_photo.return_value = True
        response = delete_photo(1, 1)
        self.assertTrue(response)


if __name__ == '__main__':
    unittest.main()
