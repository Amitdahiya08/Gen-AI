"""
Comprehensive tests for SummarizerAgent functionality.

Tests document summarization capabilities including section-wise, document-level,
and corpus-level summarization, as well as error handling and LLM integration.
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.agents.summarizer_agent import SummarizerAgent


class TestSummarizerAgent:
    """Test suite for SummarizerAgent class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = SummarizerAgent()

    def test_initialization(self):
        """Test SummarizerAgent initialization."""
        assert self.agent.system_prompt == "You are a document summarization agent."



    def test_summarize_section_success(self):
        """Test successful section summarization."""
        expected_summary = "This section discusses important concepts."

        def mock_call_llm(content):
            assert "Summarize this section:" in content
            return expected_summary

        self.agent._call_llm = mock_call_llm
        result = self.agent.summarize_section("Some section content here.")

        assert result == expected_summary

    def test_summarize_document_success(self):
        """Test successful document summarization."""
        expected_summary = "Document summary with key points."

        def mock_call_llm(content):
            assert "Provide a section-wise summary" in content
            return expected_summary

        self.agent._call_llm = mock_call_llm
        result = self.agent.summarize_document("Full document content here.")

        assert result == expected_summary

    def test_summarize_corpus_success(self):
        """Test successful corpus summarization."""
        expected_summary = "Corpus summary across multiple documents."
        texts = ["Document 1 content", "Document 2 content", "Document 3 content"]

        def mock_call_llm(content):
            assert "Summarize across documents:" in content
            assert "Document 1 content" in content
            assert "Document 2 content" in content
            assert "Document 3 content" in content
            return expected_summary

        self.agent._call_llm = mock_call_llm
        result = self.agent.summarize_corpus(texts)

        assert result == expected_summary

    def test_summarize_corpus_empty_list(self):
        """Test corpus summarization with empty document list."""
        def mock_call_llm(content):
            return "No documents to summarize."

        self.agent._call_llm = mock_call_llm
        result = self.agent.summarize_corpus([])

        assert result == "No documents to summarize."



    @patch('requests.post')
    @patch('backend.config.Config')
    def test_llm_call_api_error(self, mock_config, mock_post):
        """Test LLM API call error handling."""
        # Mock configuration
        mock_config.AZURE_OPENAI_API_KEY = "test-api-key"
        mock_config.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock_config.AZURE_OPENAI_DEPLOYMENT_NAME = "test-deployment"

        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        result = self.agent._call_llm("Test input content")

        assert "Summarization failed: Internal server error" in result

    @patch('requests.post')
    @patch('backend.config.Config')
    def test_llm_call_empty_response(self, mock_config, mock_post):
        """Test LLM API call with empty content response."""
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

        result = self.agent._call_llm("Test input content")

        assert result == "No summary generated."




