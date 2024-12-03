import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from user_settings_service import persist_user_settings, retrieve_user_settings, verify_user_presence

class TestUserSettingsService(unittest.TestCase):

    @patch('user_settings_service.get_db_connection')
    @patch('user_settings_service.verify_user_presence')
    def test_persist_user_settings_success(self, mock_verify_user_presence, mock_get_db_connection):
        mock_verify_user_presence.return_value = True
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)

        result = persist_user_settings(1, {"theme": "dark"})
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    @patch('user_settings_service.get_db_connection')
    @patch('user_settings_service.verify_user_presence')
    def test_persist_user_settings_user_not_present(self, mock_verify_user_presence, mock_get_db_connection):
        mock_verify_user_presence.return_value = False

        result = persist_user_settings(1, {"theme": "dark"})
        self.assertFalse(result)
        mock_get_db_connection.assert_not_called()

    @patch('user_settings_service.get_db_connection')
    def test_retrieve_user_settings_success(self, mock_get_db_connection):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)
        mock_cursor.fetchone.return_value = ('{"theme": "dark"}',)

        result = retrieve_user_settings(1)
        self.assertEqual(result, {"theme": "dark"})
        mock_cursor.execute.assert_called_once()

    @patch('user_settings_service.get_db_connection')
    def test_retrieve_user_settings_no_settings(self, mock_get_db_connection):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)
        mock_cursor.fetchone.return_value = (None,)

        result = retrieve_user_settings(1)
        self.assertEqual(result, {})
        mock_cursor.execute.assert_called_once()

    @patch('user_settings_service.get_db_connection')
    def test_verify_user_presence_user_exists(self, mock_get_db_connection):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)
        mock_cursor.fetchone.return_value = (1,)

        result = verify_user_presence(1)
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()

    @patch('user_settings_service.get_db_connection')
    def test_verify_user_presence_user_not_exists(self, mock_get_db_connection):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)
        mock_cursor.fetchone.return_value = (0,)

        result = verify_user_presence(1)
        self.assertFalse(result)
        mock_cursor.execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()
