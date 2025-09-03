"""
Helper utilities for the document processing platform.

This module provides utility functions for logging, MCP server integration,
and other common operations used across the platform.
"""
import datetime
import logging
from typing import Dict, Any
from langsmith import Client
from backend.config import Config

# Set up logging
logger = logging.getLogger(__name__)

# Initialize LangSmith client if API key is available
client = None
if Config.LANGCHAIN_API_KEY:
    try:
        client = Client(api_key=Config.LANGCHAIN_API_KEY)
    except Exception as e:
        logger.warning(f"Failed to initialize LangSmith client: {e}")


def log_agent_action(agent_name: str, action: str, details: str):
    """
    Log agent actions for observability and monitoring.

    This function logs agent actions to both LangSmith (if configured) and
    the standard Python logging system for comprehensive observability.

    Args:
        agent_name (str): Name of the agent performing the action
        action (str): The action being performed
        details (str): Additional details about the action

    Example:
        >>> log_agent_action("ParserAgent", "parse", "Parsed PDF document")
    """
    timestamp = datetime.datetime.utcnow().isoformat()

    # Log to standard Python logging
    logger.info(f"{agent_name} - {action}: {details[:200]}")

    # Log to LangSmith if client is available
    if client:
        try:
            client.create_run(
                name=agent_name,
                run_type="tool",   # tool, chain, llm etc.
                inputs={"action": action},
                outputs={"details": details},
                start_time=datetime.datetime.utcnow(),
                end_time=datetime.datetime.utcnow(),
            )
        except Exception as e:
            logger.warning(f"Failed to log to LangSmith: {e}")

    print(f"[LOGGED] {timestamp} - {agent_name} - {action}: {details[:200]}")


def mcp_file_save(doc_id: str, content: str) -> Dict[str, Any]:
    """
    Save document content to MCP file server.

    This function provides a stub implementation for MCP file server integration.
    In a production environment, this would connect to an actual MCP server
    for file operations.

    Args:
        doc_id (str): Unique identifier for the document
        content (str): Document content to save

    Returns:
        Dict[str, Any]: Response from the MCP server operation

    Example:
        >>> response = mcp_file_save("doc-123", "Document content...")
        >>> print(response["status"])
        "saved"
    """
    # Stub implementation - in production, this would connect to MCP server
    logger.info(f"MCP file save requested for document {doc_id}")

    try:
        # Simulate file save operation
        file_id = f"mcp-{doc_id}-{datetime.datetime.utcnow().timestamp()}"

        return {
            "status": "saved",
            "file_id": file_id,
            "doc_id": doc_id,
            "size": len(content),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"MCP file save failed for document {doc_id}: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "doc_id": doc_id
        }


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string (e.g., "1.5 MB")

    Example:
        >>> format_file_size(1536)
        "1.5 KB"
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename safe for filesystem storage

    Example:
        >>> sanitize_filename("my document?.pdf")
        "my_document.pdf"
    """
    import re
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    return sanitized if sanitized else "document"
