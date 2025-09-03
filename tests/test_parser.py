"""
Comprehensive tests for ParserAgent functionality.

Tests document parsing for various formats including PDF, DOCX, and HTML,
as well as error handling for unsupported formats and parsing failures.
"""
import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
from backend.agents.parser_agent import ParserAgent
from backend.utils.exceptions import DocumentParsingError, UnsupportedFileFormatError


class TestParserAgent:
    """Test suite for ParserAgent class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.parser = ParserAgent()

    def test_html_parser_success(self, tmp_path):
        """Test successful HTML parsing."""
        html_content = "<html><body><h1>Test Title</h1><p>Hello World</p></body></html>"
        html_file = tmp_path / "sample.html"
        html_file.write_text(html_content, encoding="utf-8")

        text = self.parser.parse(str(html_file))

        assert "Test Title" in text
        assert "Hello World" in text
        assert "<html>" not in text  # HTML tags should be stripped

    def test_html_parser_with_complex_content(self, tmp_path):
        """Test HTML parsing with complex nested content."""
        html_content = """
        <html>
            <head><title>Document Title</title></head>
            <body>
                <div class="content">
                    <h1>Main Heading</h1>
                    <p>First paragraph with <strong>bold text</strong>.</p>
                    <ul>
                        <li>Item 1</li>
                        <li>Item 2</li>
                    </ul>
                </div>
            </body>
        </html>
        """
        html_file = tmp_path / "complex.html"
        html_file.write_text(html_content, encoding="utf-8")

        text = self.parser.parse(str(html_file))

        assert "Main Heading" in text
        assert "First paragraph" in text
        assert "bold text" in text
        assert "Item 1" in text
        assert "Item 2" in text

    @patch('fitz.open')
    def test_pdf_parser_success(self, mock_fitz_open):
        """Test successful PDF parsing."""
        # Mock PDF document and page
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample PDF content\nSecond line"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        text = self.parser.parse("test.pdf")

        assert "Sample PDF content" in text
        assert "Second line" in text
        mock_fitz_open.assert_called_once_with("test.pdf")
        mock_page.get_text.assert_called_once_with("text")

    @patch('docx.Document')
    def test_docx_parser_success(self, mock_docx_document):
        """Test successful DOCX parsing."""
        # Mock DOCX document with paragraphs
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "First paragraph"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Second paragraph"
        mock_paragraph3 = MagicMock()
        mock_paragraph3.text = ""  # Empty paragraph should be filtered

        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2, mock_paragraph3]
        mock_docx_document.return_value = mock_doc

        text = self.parser.parse("test.docx")

        assert "First paragraph" in text
        assert "Second paragraph" in text
        assert text.count("\n") == 1  # Only non-empty paragraphs joined
        mock_docx_document.assert_called_once_with("test.docx")

    def test_unsupported_file_format(self):
        """Test handling of unsupported file formats."""
        with pytest.raises(UnsupportedFileFormatError) as exc_info:
            self.parser.parse("test.txt")

        assert "Unsupported file: test.txt" in str(exc_info.value)

    def test_unsupported_file_format_multiple_extensions(self):
        """Test various unsupported file extensions."""
        unsupported_files = ["test.txt", "document.rtf", "file.odt", "data.csv"]

        for filename in unsupported_files:
            with pytest.raises(UnsupportedFileFormatError):
                self.parser.parse(filename)

    @patch('fitz.open')
    def test_pdf_parsing_error(self, mock_fitz_open):
        """Test PDF parsing error handling."""
        mock_fitz_open.side_effect = Exception("PDF corruption error")

        with pytest.raises(DocumentParsingError) as exc_info:
            self.parser._parse_pdf("corrupted.pdf")

        assert "Failed parsing PDF: PDF corruption error" in str(exc_info.value)

    @patch('docx.Document')
    def test_docx_parsing_error(self, mock_docx_document):
        """Test DOCX parsing error handling."""
        mock_docx_document.side_effect = Exception("DOCX format error")

        with pytest.raises(DocumentParsingError) as exc_info:
            self.parser._parse_docx("corrupted.docx")

        assert "Failed parsing DOCX: DOCX format error" in str(exc_info.value)

    def test_html_parsing_error(self):
        """Test HTML parsing error handling."""
        with pytest.raises(DocumentParsingError) as exc_info:
            self.parser._parse_html("nonexistent.html")

        assert "Failed parsing HTML:" in str(exc_info.value)

    def test_html_parser_encoding_issues(self, tmp_path):
        """Test HTML parsing with encoding issues."""
        html_file = tmp_path / "encoded.html"
        # Write with specific encoding
        html_file.write_bytes("ñáéíóú".encode('latin-1'))

        # Should handle encoding gracefully
        try:
            text = self.parser._parse_html(str(html_file))
            # If it succeeds, that's good
            assert isinstance(text, str)
        except DocumentParsingError:
            # If it fails with our custom exception, that's also acceptable
            pass


