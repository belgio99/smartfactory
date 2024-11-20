import unittest
from unittest.mock import patch, MagicMock
import smtplib
import sys
import os
#from ..src.notification_service import send_email
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from notification_service import send_email

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

        # Call the function
        send_email('recipient@example.com', 'Test Subject', 'Test Body')

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

        # Call the function and assert exception is raised
        with self.assertRaises(Exception):
            send_email('recipient@example.com', 'Test Subject', 'Test Body')

        # Assertions
        mock_smtp.assert_called_with('smtp.example.com', 587)
        mock_server.login.assert_called_with('test@example.com', 'password')
        mock_server.send_message.assert_called()
        mock_server.quit.assert_called()

if __name__ == '__main__':
    unittest.main()