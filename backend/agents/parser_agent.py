"""
Document parsing agent for extracting text from various file formats.

This module provides the ParserAgent class which handles parsing of PDF, DOCX,
and HTML documents into plain text format for further processing by other agents.
"""
import fitz  # PyMuPDF for PDF
import docx
from bs4 import BeautifulSoup
from backend.utils.exceptions import DocumentParsingError, UnsupportedFileFormatError
from backend.utils.helpers import log_agent_action


class ParserAgent:
    """
    Document parser agent for extracting text from various file formats.

    This agent supports parsing of PDF, DOCX, and HTML documents, converting them
    into plain text format suitable for further processing by summarization,
    entity extraction, and Q&A agents.

    Supported formats:
        - PDF: Uses PyMuPDF (fitz) for text extraction
        - DOCX: Uses python-docx for Microsoft Word documents
        - HTML: Uses BeautifulSoup for HTML parsing and text extraction

    Attributes:
        None (stateless agent)

    Example:
        >>> parser = ParserAgent()
        >>> text = parser.parse("document.pdf")
        >>> print(text[:100])  # First 100 characters
    """

    def parse(self, file_path: str) -> str:
        """
        Parse a document file and extract its text content.

        This method determines the file type based on the file extension and
        delegates to the appropriate parsing method. All parsing operations
        are logged for observability.

        Args:
            file_path (str): Path to the document file to parse

        Returns:
            str: Extracted text content from the document

        Raises:
            UnsupportedFileFormatError: If the file format is not supported
            DocumentParsingError: If parsing fails due to file corruption or other issues

        Example:
            >>> parser = ParserAgent()
            >>> text = parser.parse("/path/to/document.pdf")
            >>> print(len(text))  # Length of extracted text
        """
        if file_path.endswith(".pdf"):
            text = self._parse_pdf(file_path)
        elif file_path.endswith(".docx"):
            text = self._parse_docx(file_path)
        elif file_path.endswith(".html"):
            text = self._parse_html(file_path)
        else:
            raise UnsupportedFileFormatError(f"Unsupported file: {file_path}")

        # Log the parsing action for observability (first 200 chars)
        log_agent_action("ParserAgent", "parse", text[:200])
        return text

    def _parse_pdf(self, file_path: str) -> str:
        """
        Parse a PDF file and extract its text content.

        Uses PyMuPDF (fitz) library to extract text from all pages of the PDF.
        Handles both text-based PDFs and attempts to extract text from
        image-based PDFs where possible.

        Args:
            file_path (str): Path to the PDF file

        Returns:
            str: Extracted text content from all pages

        Raises:
            DocumentParsingError: If PDF parsing fails

        Note:
            - Text from all pages is concatenated with newlines
            - Empty pages are included as newlines
            - OCR is not performed on image-only PDFs
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()  # Ensure proper cleanup
            return text.strip()
        except Exception as e:
            raise DocumentParsingError(f"Failed parsing PDF: {str(e)}")

    def _parse_docx(self, file_path: str) -> str:
        """
        Parse a DOCX file and extract its text content.

        Uses python-docx library to extract text from Microsoft Word documents.
        Extracts text from all paragraphs, excluding empty paragraphs.

        Args:
            file_path (str): Path to the DOCX file

        Returns:
            str: Extracted text content from all paragraphs

        Raises:
            DocumentParsingError: If DOCX parsing fails

        Note:
            - Only paragraph text is extracted
            - Headers, footers, and tables are not included
            - Empty paragraphs are filtered out
            - Formatting is not preserved
        """
        try:
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception as e:
            raise DocumentParsingError(f"Failed parsing DOCX: {str(e)}")

    def _parse_html(self, file_path: str) -> str:
        """
        Parse an HTML file and extract its text content.

        Uses BeautifulSoup to parse HTML and extract clean text content,
        removing all HTML tags and formatting while preserving text structure.

        Args:
            file_path (str): Path to the HTML file

        Returns:
            str: Extracted text content with HTML tags removed

        Raises:
            DocumentParsingError: If HTML parsing fails

        Note:
            - All HTML tags are removed
            - Text is separated by newlines where appropriate
            - Encoding is assumed to be UTF-8
            - JavaScript and CSS content is excluded
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            return soup.get_text(separator="\n")
        except Exception as e:
            raise DocumentParsingError(f"Failed parsing HTML: {str(e)}")
