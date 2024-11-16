# Test Suite
import unittest
from unittest.mock import patch, MagicMock, call
from main import send_mail, read_inbox, view_sent_inbox, tag_email, view_tagged_inbox, delete_email

class NotionEmailServiceTests(unittest.TestCase):
    def setUp(self):
        # Use a consistent test email structure with a valid UUID format for test page ID
        self.test_email = {
            "id": "00000000-0000-0000-0000-000000000000",
            "properties": {
                "Message": {
                    "title": [{"text": {"content": "[general] [2024-01-01 12:00:00] Test message"}}]
                },
                "Sender": {
                    "rich_text": [{"text": {"content": "test_sender"}}]
                },
                "Recipient": {
                    "rich_text": [{"text": {"content": "test_recipient"}}]
                }
            }
        }

    @patch("main.notion.pages.create")
    def test_send_mail(self, mock_create):
        """Test sending an email"""
        mock_create.return_value = {"id": "mock_page_id"}

        # Test valid email sending
        result = send_mail("sender", "recipient", "Test message")
        self.assertIsNotNone(result)
        mock_create.assert_called_once()

        # Test invalid input
        with self.assertRaises(ValueError):
            send_mail("", "recipient", "Test message")

    @patch("main.notion.pages.create")
    def test_message_format(self, mock_create):
        """Test message format in sent emails"""
        mock_create.return_value = {"id": "mock_page_id"}
        sender = "test_sender"
        recipient = "test_recipient"
        message = "Test message"
        
        # Call the function being tested
        send_mail(sender, recipient, message)
        
        # Verify that create was called with expected properties
        self.assertTrue(mock_create.called)
        
        # Get the call arguments
        properties = mock_create.call_args[1]["properties"]
        
        # Verify the structure and content of the properties
        self.assertIn("Message", properties)
        self.assertIn("Sender", properties)
        self.assertIn("Recipient", properties)
        self.assertEqual(properties["Sender"]["rich_text"][0]["text"]["content"], sender)
        self.assertEqual(properties["Recipient"]["rich_text"][0]["text"]["content"], recipient)
        self.assertIn(message, properties["Message"]["title"][0]["text"]["content"])

    @patch("main.notion.databases.query")
    def test_read_inbox(self, mock_query):
        """Test reading inbox"""
        mock_query.return_value = {"results": [self.test_email]}

        # Capture printed output
        with patch('builtins.print') as mock_print:
            read_inbox("test_recipient")
            mock_print.assert_called()

    @patch("main.notion.databases.query")
    def test_view_sent_inbox(self, mock_query):
        """Test viewing sent emails"""
        mock_query.return_value = {"results": [self.test_email]}

        with patch('builtins.print') as mock_print:
            view_sent_inbox("test_sender")
            mock_print.assert_called()

    @patch("main.notion.pages.update")
    @patch("main.notion.databases.query")
    def test_tag_email(self, mock_query, mock_update):
        """Test tagging emails"""
        mock_query.return_value = {"results": [self.test_email]}
        mock_update.return_value = {"id": "mock_page_id"}

        # Mock user input for tag selection
        with patch('builtins.input', side_effect=["1", "work"]), patch('builtins.print') as mock_print:
            tag_email("test_recipient")
            mock_print.assert_called()
            mock_update.assert_called_once()  # Ensures the update was "called" without real API

    @patch("main.notion.pages.update")
    @patch("main.notion.databases.query")
    def test_delete_email(self, mock_query, mock_update):
        """Test deleting emails"""
        mock_query.return_value = {"results": [self.test_email]}
        mock_update.return_value = {"id": "mock_page_id"}

        # Mock user input for deletion
        with patch('builtins.input', return_value="1"), patch('builtins.print') as mock_print:
            delete_email("test_user")
            mock_print.assert_called()
            mock_update.assert_called_once()  # Ensures the update was "called" without real API

    @patch("main.notion.databases.query")
    def test_empty_inbox(self, mock_query):
        """Test reading empty inbox"""
        mock_query.return_value = {"results": []}

        with patch('builtins.print') as mock_print:
            read_inbox("test_recipient")
            mock_print.assert_called_with("Inbox for test_recipient:")

    @patch("main.notion.databases.query")
    def test_invalid_tag(self, mock_query):
        """Test invalid tag input"""
        mock_query.return_value = {"results": [self.test_email]}

        with patch('builtins.input', side_effect=["1", "invalid_tag"]), patch('builtins.print') as mock_print:
            tag_email("test_recipient")
            mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()


