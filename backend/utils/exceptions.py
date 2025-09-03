class DocumentParsingError(Exception):
    """Raised when a document cannot be parsed"""

class UnsupportedFileFormatError(Exception):
    """Raised for unsupported file formats"""

class ProcessingError(Exception):
    """Raised for generic processing issues"""
