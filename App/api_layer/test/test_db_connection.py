import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/database')))

from connection import get_db_connection, query_db, query_db_with_params, close_connection

class TestDatabaseUtils(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        # Mock connection and cursor objects
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Call the function
        connection, cursor = get_db_connection()

        # Assertions
        self.assertIsNotNone(connection)
        self.assertIsNotNone(cursor)
        mock_connect.assert_called_once()
        mock_connection.cursor.assert_called_once()

    @patch('psycopg2.connect', side_effect=Exception("Database connection failed"))
    def test_get_db_connection_failure(self, mock_connect):
        # Call the function
        connection, cursor = get_db_connection()

        # Assertions
        self.assertIsNone(connection)
        self.assertIsNone(cursor)

    @patch('psycopg2.connect')
    def test_query_db_success(self, mock_connect):
        # Mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Call the function
        connection, cursor = get_db_connection()
        query = "SELECT * FROM users;"
        result = query_db(cursor, connection, query)

        # Assertions
        mock_cursor.execute.assert_called_once_with(query)
        mock_connection.commit.assert_called_once()
        self.assertIsNone(result)  # cursor.execute returns None

    @patch('psycopg2.connect')
    def test_query_db_with_params_success(self, mock_connect):
        # Mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Set up fetchall to return mock data
        mock_cursor.fetchall.return_value = [("John", "Doe")]

        # Call the function
        connection, cursor = get_db_connection()
        query = "SELECT * FROM users WHERE id = %s;"
        params = (1,)
        result = query_db_with_params(cursor, connection, query, params)

        # Assertions
        mock_cursor.execute.assert_called_once_with(query, params)
        mock_connection.commit.assert_called_once()
        self.assertEqual(result, [("John", "Doe")])

    @patch('psycopg2.connect')
    def test_query_db_with_params_failure(self, mock_connect):
        # Mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Make execute raise an exception
        mock_cursor.execute.side_effect = Exception("Query failed")

        # Call the function
        connection, cursor = get_db_connection()
        query = "SELECT * FROM users WHERE id = %s;"
        params = (1,)
        result = query_db_with_params(cursor, connection, query, params)

        # Assertions
        self.assertIsNone(result)
        mock_cursor.execute.assert_called_once_with(query, params)

    @patch('psycopg2.connect')
    def test_close_connection(self, mock_connect):
        # Mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        # Call the function
        close_connection(mock_connection, mock_cursor)

        # Assertions
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

# Run the tests
if __name__ == '__main__':
    unittest.main()
