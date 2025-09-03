"""
FastAPI application with global exception handling.

This module sets up the main FastAPI application with comprehensive error handling,
logging, and route configuration for the document summarization and Q&A platform.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

from backend.logging_config import setup_logging
from backend.routes import documents, summary, qa, mcp
from backend.utils.exceptions import (
    DocumentParsingError,
    UnsupportedFileFormatError,
    ProcessingError
)

logger = setup_logging()

app = FastAPI(
    title="Intelligent Document Summarization & Q&A",
    description="AI-powered document processing platform with summarization, entity extraction, and Q&A capabilities",
    version="1.0.0"
)


# Global exception handlers
@app.exception_handler(DocumentParsingError)
async def document_parsing_error_handler(request: Request, exc: DocumentParsingError):
    """Handle document parsing errors."""
    logger.error(f"Document parsing error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Document Parsing Error",
            "message": str(exc),
            "type": "document_parsing_error"
        }
    )


@app.exception_handler(UnsupportedFileFormatError)
async def unsupported_file_format_error_handler(request: Request, exc: UnsupportedFileFormatError):
    """Handle unsupported file format errors."""
    logger.error(f"Unsupported file format error: {str(exc)}")
    return JSONResponse(
        status_code=415,
        content={
            "error": "Unsupported File Format",
            "message": str(exc),
            "type": "unsupported_file_format_error"
        }
    )


@app.exception_handler(ProcessingError)
async def processing_error_handler(request: Request, exc: ProcessingError):
    """Handle general processing errors."""
    logger.error(f"Processing error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Processing Error",
            "message": str(exc),
            "type": "processing_error"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors(),
            "type": "validation_error"
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail,
            "type": "http_error"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "type": "internal_server_error"
        }
    )


# Include routers
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(summary.router, prefix="/summary", tags=["Summary"])
app.include_router(qa.router, prefix="/qa", tags=["Q&A"])
app.include_router(mcp.router, prefix="/mcp", tags=["MCP"])


@app.get("/")
async def root():
    """Root endpoint providing API status information."""
    return {
        "message": "Intelligent Document Summarization & Q&A API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "document-summarization-api",
        "version": "1.0.0"
    }
