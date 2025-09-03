"""
Comprehensive tests for API routes functionality.

Tests FastAPI endpoints including document upload, summary retrieval,
Q&A functionality, and MCP server endpoints.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
from io import BytesIO

# Import the FastAPI app
from backend.main import app
from backend.routes.documents import documents_store


class TestDocumentRoutes:
    """Test suite for document-related API routes."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        # Clear the documents store before each test
        documents_store.clear()

    def teardown_method(self):
        """Clean up after each test method."""
        # Clear the documents store after each test
        documents_store.clear()

    @patch('backend.agents.parser_agent.ParserAgent.parse')
    @patch('backend.agents.summarizer_agent.SummarizerAgent.summarize_document')
    @patch('backend.agents.entity_agent.EntityAgent.extract')
    @patch('backend.agents.validation_agent.ValidationAgent.validate_summary')
    @patch('backend.agents.validation_agent.ValidationAgent.validate_entities')
    def test_upload_document_success(self, mock_validate_entities, mock_validate_summary,
                                   mock_extract, mock_summarize, mock_parse):
        """Test successful document upload."""
        # Mock agent responses
        mock_parse.return_value = "Parsed document content"
        mock_summarize.return_value = "Document summary"
        mock_extract.return_value = {"names": ["John Doe"], "dates": ["2023-01-01"], "organizations": ["Test Corp"]}
        mock_validate_summary.return_value = True
        mock_validate_entities.return_value = True

        # Create a test file
        test_content = b"Test PDF content"
        files = {"file": ("test.pdf", BytesIO(test_content), "application/pdf")}

        response = self.client.post("/documents/upload", files=files)

        assert response.status_code == 200
        data = response.json()

        assert "doc_id" in data
        assert data["filename"] == "test.pdf"
        assert data["summary"] == "Document summary"
        assert data["entities"]["names"] == ["John Doe"]

        # Verify document is stored
        assert len(documents_store) == 1
        doc_id = data["doc_id"]
        assert doc_id in documents_store
        assert documents_store[doc_id]["filename"] == "test.pdf"
        assert documents_store[doc_id]["text"] == "Parsed document content"



    @patch('backend.agents.parser_agent.ParserAgent.parse')
    @patch('backend.agents.summarizer_agent.SummarizerAgent.summarize_document')
    @patch('backend.agents.entity_agent.EntityAgent.extract')
    @patch('backend.agents.validation_agent.ValidationAgent.validate_summary')
    @patch('backend.agents.validation_agent.ValidationAgent.validate_entities')
    @patch('backend.agents.validation_agent.ValidationAgent.rollback_summary')
    def test_upload_document_summary_validation_failure(self, mock_rollback_summary, mock_validate_entities,
                                                       mock_validate_summary, mock_extract, mock_summarize, mock_parse):
        """Test document upload with summary validation failure."""
        # Mock agent responses
        mock_parse.return_value = "Parsed document content"
        mock_summarize.return_value = "Bad summary"
        mock_extract.return_value = {"names": [], "dates": [], "organizations": []}
        mock_validate_summary.return_value = False  # Summary validation fails
        mock_validate_entities.return_value = True
        mock_rollback_summary.return_value = "Summary rolled back due to low quality."

        # Create a test file
        test_content = b"Test PDF content"
        files = {"file": ("test.pdf", BytesIO(test_content), "application/pdf")}

        response = self.client.post("/documents/upload", files=files)

        assert response.status_code == 200
        data = response.json()

        assert data["summary"] == "Summary rolled back due to low quality."
        mock_rollback_summary.assert_called_once()

    @patch('backend.agents.parser_agent.ParserAgent.parse')
    @patch('backend.agents.summarizer_agent.SummarizerAgent.summarize_document')
    @patch('backend.agents.entity_agent.EntityAgent.extract')
    @patch('backend.agents.validation_agent.ValidationAgent.validate_summary')
    @patch('backend.agents.validation_agent.ValidationAgent.validate_entities')
    @patch('backend.agents.validation_agent.ValidationAgent.rollback_entities')
    def test_upload_document_entity_validation_failure(self, mock_rollback_entities, mock_validate_entities,
                                                      mock_validate_summary, mock_extract, mock_summarize, mock_parse):
        """Test document upload with entity validation failure."""
        # Mock agent responses
        mock_parse.return_value = "Parsed document content"
        mock_summarize.return_value = "Good summary"
        mock_extract.return_value = {"names": [], "dates": [], "organizations": []}
        mock_validate_summary.return_value = True
        mock_validate_entities.return_value = False  # Entity validation fails
        mock_rollback_entities.return_value = "Entities rolled back due to low confidence."

        # Create a test file
        test_content = b"Test PDF content"
        files = {"file": ("test.pdf", BytesIO(test_content), "application/pdf")}

        response = self.client.post("/documents/upload", files=files)

        assert response.status_code == 200
        data = response.json()

        assert data["entities"]["error"] == "Entities rolled back due to low confidence."
        mock_rollback_entities.assert_called_once()


class TestSummaryRoutes:
    """Test suite for summary-related API routes."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        # Clear and populate test data
        documents_store.clear()
        documents_store["test-doc-id"] = {
            "filename": "test.pdf",
            "text": "Test document content",
            "summary": "Original summary",
            "entities": {"names": ["John Doe"], "dates": [], "organizations": []}
        }

    def teardown_method(self):
        """Clean up after each test method."""
        documents_store.clear()

    def test_get_summary_success(self):
        """Test successful summary retrieval."""
        response = self.client.get("/summary/test-doc-id")

        assert response.status_code == 200
        data = response.json()

        assert data["doc_id"] == "test-doc-id"
        assert data["summary"] == "Original summary"



    def test_update_summary_success(self):
        """Test successful summary update."""
        updated_summary = "This is the updated summary content."

        response = self.client.post(
            "/summary/test-doc-id/update",
            json={"updated_summary": updated_summary}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["doc_id"] == "test-doc-id"
        assert data["summary"] == updated_summary
        assert data["status"] == "updated"

        # Verify the summary was actually updated in storage
        assert documents_store["test-doc-id"]["summary"] == updated_summary




class TestQARoutes:
    """Test suite for Q&A-related API routes."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        # Clear and populate test data
        documents_store.clear()
        documents_store["test-doc-id"] = {
            "filename": "test.pdf",
            "text": "This document contains information about artificial intelligence and machine learning.",
            "summary": "AI/ML document summary",
            "entities": {"names": ["John Doe"], "dates": [], "organizations": []}
        }

    def teardown_method(self):
        """Clean up after each test method."""
        documents_store.clear()

    @patch('backend.agents.qa_agent.QAAgent.ask')
    def test_ask_question_success(self, mock_ask):
        """Test successful Q&A interaction."""
        mock_ask.return_value = "This document is about artificial intelligence and machine learning."

        response = self.client.get("/qa/", params={
            "doc_id": "test-doc-id",
            "question": "What is this document about?"
        })

        assert response.status_code == 200
        data = response.json()

        assert data["doc_id"] == "test-doc-id"
        assert data["question"] == "What is this document about?"
        assert data["answer"] == "This document is about artificial intelligence and machine learning."

        # Verify the QA agent was called with correct parameters
        mock_ask.assert_called_once_with(
            "What is this document about?",
            "This document contains information about artificial intelligence and machine learning."
        )



    def test_ask_question_missing_question_param(self):
        """Test Q&A without question parameter."""
        response = self.client.get("/qa/", params={
            "doc_id": "test-doc-id"
        })

        assert response.status_code == 422  # Validation error for missing required parameter


class TestMCPRoutes:
    """Test suite for MCP server-related API routes."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        # Clear and populate test data
        documents_store.clear()
        documents_store["test-doc-id"] = {
            "filename": "test.pdf",
            "text": "This is test document content for MCP operations.",
            "summary": "Test summary",
            "entities": {"names": ["John Doe"], "dates": [], "organizations": []}
        }

    def teardown_method(self):
        """Clean up after each test method."""
        documents_store.clear()



    def test_search_docs_success(self):
        """Test successful document search."""
        # Add another document for search testing
        documents_store["test-doc-id-2"] = {
            "filename": "another.pdf",
            "text": "This document discusses machine learning algorithms.",
            "summary": "ML algorithms summary",
            "entities": {"names": [], "dates": [], "organizations": []}
        }

        response = self.client.get("/mcp/search", params={"query": "machine learning"})

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "machine learning"
        assert len(data["results"]) == 1
        assert data["results"][0]["doc_id"] == "test-doc-id-2"
        assert data["results"][0]["filename"] == "another.pdf"

    def test_search_docs_no_results(self):
        """Test document search with no matching results."""
        response = self.client.get("/mcp/search", params={"query": "nonexistent topic"})

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "nonexistent topic"
        assert len(data["results"]) == 0

    def test_search_docs_case_insensitive(self):
        """Test that document search is case insensitive."""
        response = self.client.get("/mcp/search", params={"query": "TEST DOCUMENT"})

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "TEST DOCUMENT"
        assert len(data["results"]) == 1
        assert data["results"][0]["doc_id"] == "test-doc-id"


class TestRootRoute:
    """Test suite for root API route."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test the root API endpoint."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "Intelligent Document Summarization & Q&A API is running" in data["message"]