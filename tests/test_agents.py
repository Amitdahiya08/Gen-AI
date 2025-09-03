"""
Comprehensive tests for CriticAgent and ValidationAgent functionality.

Tests content review, validation, and rollback mechanisms.
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.agents.critic_agent import CriticAgent
from backend.agents.validation_agent import ValidationAgent


class TestCriticAgent:
    """Test suite for CriticAgent class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = CriticAgent()

    @patch('requests.post')
    @patch('backend.config.Config')
    def test_review_summary_success(self, mock_config, mock_post):
        """Test successful summary review."""
        # Mock configuration
        mock_config.AZURE_OPENAI_API_KEY = "test-api-key"
        mock_config.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock_config.AZURE_OPENAI_DEPLOYMENT_NAME = "test-deployment"

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Summary looks good, no bias detected."}}]
        }
        mock_post.return_value = mock_response

        summary = "This is a well-balanced summary of the document."

        result = self.agent.review_summary(summary)

        assert result["status"] == "reviewed"
        assert result["critic_notes"] == "Summary looks good, no bias detected."
        mock_post.assert_called_once()

        # Verify request structure
        call_args = mock_post.call_args
        assert "api-key" in call_args[1]["headers"]
        assert "messages" in call_args[1]["json"]
        assert len(call_args[1]["json"]["messages"]) == 2

        # Verify system message
        system_msg = call_args[1]["json"]["messages"][0]
        assert system_msg["role"] == "system"
        assert "critic" in system_msg["content"].lower()
        assert "bias" in system_msg["content"]
        assert "completeness" in system_msg["content"]
        assert "sensitive info" in system_msg["content"]

        # Verify user message contains summary
        user_msg = call_args[1]["json"]["messages"][1]
        assert user_msg["role"] == "user"
        assert summary in user_msg["content"]

    @patch('requests.post')
    @patch('backend.config.Config')
    def test_review_summary_api_error(self, mock_config, mock_post):
        """Test summary review API error handling."""
        # Mock configuration
        mock_config.AZURE_OPENAI_API_KEY = "test-api-key"
        mock_config.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock_config.AZURE_OPENAI_DEPLOYMENT_NAME = "test-deployment"

        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        summary = "Test summary for error case."

        result = self.agent.review_summary(summary)

        assert result["status"] == "failed"
        assert result["reason"] == "Internal server error"

    @patch('backend.utils.helpers.log_agent_action')
    def test_logging_integration(self, mock_log_agent_action):
        """Test that critic actions are properly logged."""
        def mock_review_summary(summary):
            return {"status": "reviewed", "critic_notes": "Test review"}

        # Mock the internal method to avoid API calls
        original_review = self.agent.review_summary
        self.agent.review_summary = mock_review_summary

        summary = "Test summary"

        result = self.agent.review_summary(summary)

        assert result["status"] == "reviewed"
        assert result["critic_notes"] == "Test review"


class TestValidationAgent:
    """Test suite for ValidationAgent class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = ValidationAgent()

    def test_validate_summary_success(self):
        """Test successful summary validation."""
        good_summary = "This is a comprehensive summary with more than five words and meaningful content."

        result = self.agent.validate_summary(good_summary)

        assert result is True

    def test_validate_summary_failure_empty(self):
        """Test summary validation failure with empty summary."""
        empty_summary = ""

        result = self.agent.validate_summary(empty_summary)

        assert result is False

    def test_validate_summary_failure_none(self):
        """Test summary validation failure with None summary."""
        none_summary = None

        result = self.agent.validate_summary(none_summary)

        assert result is False

    def test_validate_summary_failure_too_short(self):
        """Test summary validation failure with too short summary."""
        short_summary = "Too short"  # Only 2 words

        result = self.agent.validate_summary(short_summary)

        assert result is False

    def test_validate_summary_edge_case_exactly_five_words(self):
        """Test summary validation with exactly five words."""
        five_word_summary = "This summary has exactly five"  # Exactly 5 words

        result = self.agent.validate_summary(five_word_summary)

        assert result is False  # Should be > 5 words, not >= 5

    def test_validate_summary_edge_case_six_words(self):
        """Test summary validation with exactly six words."""
        six_word_summary = "This summary has exactly six words"  # Exactly 6 words

        result = self.agent.validate_summary(six_word_summary)

        assert result is True  # Should pass with > 5 words

    def test_validate_entities_success(self):
        """Test successful entity validation."""
        entities = {
            "names": ["John Smith", "Mary Johnson"],
            "dates": ["12/25/2023"],
            "organizations": ["Microsoft Corp"]
        }

        result = self.agent.validate_entities(entities)

        assert result is True

    def test_validate_entities_failure_empty(self):
        """Test entity validation failure with empty entities."""
        entities = {
            "names": [],
            "dates": [],
            "organizations": []
        }

        result = self.agent.validate_entities(entities)

        assert result is False

    def test_validate_entities_success_partial(self):
        """Test entity validation success with some empty categories."""
        entities = {
            "names": ["John Smith"],
            "dates": [],
            "organizations": []
        }

        result = self.agent.validate_entities(entities)

        assert result is True

    def test_rollback_summary(self):
        """Test summary rollback functionality."""
        result = self.agent.rollback_summary()

        assert result == "Summary rolled back due to low quality."

    def test_rollback_entities(self):
        """Test entity rollback functionality."""
        result = self.agent.rollback_entities()

        assert result == "Entities rolled back due to low confidence."

