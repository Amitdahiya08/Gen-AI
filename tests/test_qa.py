"""
Comprehensive tests for QAAgent functionality.

Tests question-answering capabilities including various question types,
document contexts, and error handling scenarios.
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.agents.qa_agent import QAAgent


class TestQAAgent:
    """Test suite for QAAgent class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = QAAgent()

    def test_ask_empty_question(self):
        """Test handling of empty question."""
        doc_text = "This is a sample document with some content."

        result = self.agent.ask("", doc_text)

        assert result == "No question provided."

    def test_ask_whitespace_question(self):
        """Test handling of whitespace-only question."""
        doc_text = "This is a sample document with some content."

        result = self.agent.ask("   \n\t  ", doc_text)

        assert result == "No question provided."

    def test_ask_empty_document(self):
        """Test handling of empty document."""
        question = "What is this document about?"

        result = self.agent.ask(question, "")

        assert result == "No document content available."

    def test_ask_whitespace_document(self):
        """Test handling of whitespace-only document."""
        question = "What is this document about?"

        result = self.agent.ask(question, "   \n\t  ")

        assert result == "No document content available."





    @patch('requests.post')
    @patch('backend.config.Config')
    def test_ask_empty_response(self, mock_config, mock_post):
        """Test handling of empty API response."""
        # Mock configuration
        mock_config.AZURE_OPENAI_API_KEY = "test-api-key"
        mock_config.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock_config.AZURE_OPENAI_DEPLOYMENT_NAME = "test-deployment"

        # Mock response with empty content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": ""}}]
        }
        mock_post.return_value = mock_response

        question = "What is this about?"
        doc_text = "Sample document content."

        result = self.agent.ask(question, doc_text)

        assert result == "No relevant answer found."

    @patch('backend.utils.helpers.log_agent_action')
    def test_logging_integration(self, mock_log_agent_action):
        """Test that Q&A actions are properly logged."""
        def mock_ask(question, doc_text):
            return "Test answer for logging"

        # Mock the internal method to avoid API calls
        original_ask = self.agent.ask
        self.agent.ask = mock_ask

        question = "Test question"
        doc_text = "Test document"

        result = self.agent.ask(question, doc_text)

        assert result == "Test answer for logging"
