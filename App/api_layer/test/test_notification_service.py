import unittest
from unittest.mock import patch, MagicMock
import smtplib
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from notification_service import send_email, save_alert, retrieve_alerts

class TestSendEmail(unittest.TestCase):

    @patch('notification_service.smtplib.SMTP')
    @patch('notification_service.os.getenv')
    def test_send_email_success(self, mock_getenv, mock_smtp):
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            'SMTP_EMAIL': 'test@example.com',
            'SMTP_PASSWORD': 'password',
            'SMTP_SERVER': 'smtp.example.com',
            'SMTP_PORT': '587'
        }[key]

        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Create a mock alert
        alert = MagicMock()
        alert.alertId = '1'
        alert.title = 'Test Alert'
        alert.type = 'Error'
        alert.description = 'This is a test alert'
        alert.triggeredAt = '2023-10-10 10:00:00'
        alert.machineName = 'Machine1'
        alert.isPush = True
        alert.recipients = ['recipient@example.com']
        alert.severity.value = 'High'

        # Call the function
        send_email('recipient@example.com', alert)

        # Assertions
        mock_smtp.assert_called_with('smtp.example.com', 587)
        mock_server.login.assert_called_with('test@example.com', 'password')
        mock_server.send_message.assert_called()
        mock_server.quit.assert_called()

    @patch('notification_service.smtplib.SMTP')
    @patch('notification_service.os.getenv')
    def test_send_email_failure(self, mock_getenv, mock_smtp):
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            'SMTP_EMAIL': 'test@example.com',
            'SMTP_PASSWORD': 'password',
            'SMTP_SERVER': 'smtp.example.com',
            'SMTP_PORT': '587'
        }[key]

        # Mock SMTP server to raise an exception
        mock_server = MagicMock()
        mock_server.send_message.side_effect = smtplib.SMTPException("Failed to send email")
        mock_smtp.return_value = mock_server

        # Create a mock alert
        alert = MagicMock()
        alert.alertId = '1'
        alert.title = 'Test Alert'
        alert.type = 'Error'
        alert.description = 'This is a test alert'
        alert.triggeredAt = '2023-10-10 10:00:00'
        alert.machineName = 'Machine1'
        alert.isPush = True
        alert.recipients = ['recipient@example.com']
        alert.severity.value = 'High'

        # Call the function and assert exception is raised
        with self.assertRaises(Exception):
            send_email('recipient@example.com', alert)

        # Assertions
        mock_smtp.assert_called_with('smtp.example.com', 587)
        mock_server.login.assert_called_with('test@example.com', 'password')
        mock_server.send_message.assert_called()
        mock_server.quit.assert_called()

class TestSaveAlert(unittest.TestCase):

    @patch('notification_service.get_db_connection')
    @patch('notification_service.query_db')
    def test_save_alert_success(self, mock_query_db, mock_get_db_connection):
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)

        # Create a mock alert
        alert = MagicMock()
        alert.alertId = '1'
        alert.title = 'Test Alert'
        alert.type = 'Error'
        alert.description = 'This is a test alert'
        alert.triggeredAt = '2023-10-10 10:00:00'
        alert.machineName = 'Machine1'
        alert.isPush = True
        alert.recipients = ['user1@example.com']
        alert.severity.value = 'High'

        # Call the function
        save_alert(alert)

        # Assertions
        mock_query_db.assert_called()
        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()

    @patch('notification_service.get_db_connection')
    @patch('notification_service.query_db')
    def test_save_alert_failure(self, mock_query_db, mock_get_db_connection):
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)

        # Mock query_db to raise an exception
        mock_query_db.side_effect = Exception("Database error")

        # Create a mock alert
        alert = MagicMock()
        alert.alertId = '1'
        alert.title = 'Test Alert'
        alert.type = 'Error'
        alert.description = 'This is a test alert'
        alert.triggeredAt = '2023-10-10 10:00:00'
        alert.machineName = 'Machine1'
        alert.isPush = True
        alert.recipients = ['user1@example.com']
        alert.severity.value = 'High'

        # Call the function and assert exception is raised
        with self.assertRaises(Exception):
            save_alert(alert)

        # Assertions
        mock_query_db.assert_called()
        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()

class TestRetrieveAlerts(unittest.TestCase):

    @patch('notification_service.get_db_connection')
    def test_retrieve_alerts_success(self, mock_get_db_connection):
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)

        # Mock database response
        mock_cursor.fetchall.return_value = [
            ('1', 'Test Alert', 'Error', 'This is a test alert', '2023-10-10 10:00:00', 'Machine1', 1, '["user1@example.com"]', 'High')
        ]

        # Call the function
        alerts = retrieve_alerts('user1@example.com')

        # Assertions
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['alertId'], '1')
        self.assertEqual(alerts[0]['title'], 'Test Alert')
        self.assertEqual(alerts[0]['description'], 'This is a test alert')

        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()

    @patch('notification_service.get_db_connection')
    def test_retrieve_alerts_failure(self, mock_get_db_connection):
        # Mock database connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = (mock_connection, mock_cursor)

        # Mock cursor to raise an exception
        mock_cursor.execute.side_effect = Exception("Database error")

        # Call the function and assert exception is raised
        with self.assertRaises(Exception):
            retrieve_alerts('user1@example.com')

        # Assertions
        mock_cursor.close.assert_called()
        mock_connection.close.assert_called()

if __name__ == '__main__':
    unittest.main()