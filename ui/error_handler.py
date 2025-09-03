"""
Global error handling utilities for Streamlit UI.

This module provides centralized error handling, logging, and user-friendly
error display functionality for the Streamlit application.
"""
import streamlit as st
import traceback
import logging
from functools import wraps
from typing import Callable, Any
import requests


# Set up logging for UI errors
logging.basicConfig(level=logging.INFO)
ui_logger = logging.getLogger("streamlit-ui")


def handle_api_error(response: requests.Response) -> str:
    """
    Handle API error responses and return user-friendly error messages.
    
    Args:
        response: The HTTP response object from an API call
        
    Returns:
        str: User-friendly error message
    """
    try:
        error_data = response.json()
        if isinstance(error_data, dict):
            error_type = error_data.get("type", "unknown_error")
            message = error_data.get("message", "An error occurred")
            
            # Map error types to user-friendly messages
            error_messages = {
                "document_parsing_error": f"📄 Document Parsing Error: {message}",
                "unsupported_file_format_error": f"❌ Unsupported File Format: {message}",
                "processing_error": f"⚠️ Processing Error: {message}",
                "validation_error": f"📝 Validation Error: {message}",
                "http_error": f"🌐 Network Error: {message}",
                "internal_server_error": "🔧 Server Error: Something went wrong on our end. Please try again later."
            }
            
            return error_messages.get(error_type, f"❌ Error: {message}")
        else:
            return f"❌ Server Error: {response.text}"
    except Exception:
        return f"❌ Network Error: Unable to connect to server (Status: {response.status_code})"


def display_error(error_message: str, error_type: str = "error"):
    """
    Display error message in Streamlit with appropriate styling.
    
    Args:
        error_message: The error message to display
        error_type: Type of error ('error', 'warning', 'info')
    """
    if error_type == "error":
        st.error(error_message)
    elif error_type == "warning":
        st.warning(error_message)
    elif error_type == "info":
        st.info(error_message)
    else:
        st.error(error_message)


def display_success(message: str):
    """
    Display success message in Streamlit.
    
    Args:
        message: The success message to display
    """
    st.success(message)


def safe_api_call(func: Callable) -> Callable:
    """
    Decorator to safely handle API calls with proper error handling.
    
    Args:
        func: Function that makes API calls
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            display_error("🔌 Connection Error: Unable to connect to the backend server. Please ensure the server is running.")
            return None
        except requests.exceptions.Timeout:
            display_error("⏱️ Timeout Error: The request took too long. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            display_error(f"🌐 Network Error: {str(e)}")
            return None
        except Exception as e:
            ui_logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            ui_logger.error(f"Traceback: {traceback.format_exc()}")
            display_error(f"❌ Unexpected Error: {str(e)}")
            return None
    
    return wrapper


def safe_streamlit_component(func: Callable) -> Callable:
    """
    Decorator to safely handle Streamlit component rendering with error boundaries.
    
    Args:
        func: Streamlit component function
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ui_logger.error(f"Error in Streamlit component {func.__name__}: {str(e)}")
            ui_logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Display error in a contained way
            with st.container():
                st.error(f"❌ Component Error: Unable to render {func.__name__}")
                
                # Show details in an expander for debugging
                with st.expander("🔍 Error Details (for debugging)"):
                    st.code(f"Error: {str(e)}")
                    st.code(f"Function: {func.__name__}")
                    if st.checkbox("Show full traceback"):
                        st.code(traceback.format_exc())
            
            return None
    
    return wrapper


def handle_file_upload_error(error: Exception) -> str:
    """
    Handle file upload specific errors.
    
    Args:
        error: The exception that occurred during file upload
        
    Returns:
        str: User-friendly error message
    """
    error_str = str(error).lower()
    
    if "file too large" in error_str or "size" in error_str:
        return "📁 File Too Large: Please upload a smaller file (max 10MB recommended)"
    elif "format" in error_str or "type" in error_str:
        return "📄 Invalid Format: Please upload a PDF, DOCX, or HTML file"
    elif "corrupt" in error_str or "damaged" in error_str:
        return "🔧 Corrupted File: The file appears to be damaged. Please try a different file"
    elif "permission" in error_str or "access" in error_str:
        return "🔒 Access Error: Unable to read the file. Please check file permissions"
    else:
        return f"📁 Upload Error: {str(error)}"


def create_error_boundary():
    """
    Create a global error boundary for the Streamlit app.
    This should be called at the top level of the main app.
    """
    if "error_boundary_initialized" not in st.session_state:
        st.session_state.error_boundary_initialized = True
        
        # Set up global error handling
        def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions in Streamlit."""
            if exc_type is KeyboardInterrupt:
                return
            
            ui_logger.error(f"Uncaught exception: {exc_type.__name__}: {exc_value}")
            ui_logger.error(f"Traceback: {''.join(traceback.format_tb(exc_traceback))}")
            
            # Store error in session state to display in UI
            st.session_state.global_error = {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "traceback": traceback.format_exc()
            }
        
        # Note: In Streamlit, we can't directly set sys.excepthook
        # Instead, we'll use try-catch blocks in components


def display_global_error():
    """
    Display any global errors stored in session state.
    This should be called in the main app after create_error_boundary().
    """
    if "global_error" in st.session_state:
        error_info = st.session_state.global_error
        
        st.error("🚨 Application Error")
        st.write("An unexpected error occurred in the application.")
        
        with st.expander("🔍 Error Details"):
            st.write(f"**Error Type:** {error_info['type']}")
            st.write(f"**Message:** {error_info['message']}")
            
            if st.checkbox("Show technical details"):
                st.code(error_info['traceback'])
        
        if st.button("🔄 Clear Error and Refresh"):
            del st.session_state.global_error
            st.rerun()


def log_user_action(action: str, details: str = ""):
    """
    Log user actions for monitoring and debugging.
    
    Args:
        action: The action performed by the user
        details: Additional details about the action
    """
    ui_logger.info(f"User action: {action} | Details: {details}")


# Context manager for safe operations
class SafeOperation:
    """Context manager for safe operations with error handling."""
    
    def __init__(self, operation_name: str, show_spinner: bool = True):
        self.operation_name = operation_name
        self.show_spinner = show_spinner
        self.spinner = None
    
    def __enter__(self):
        if self.show_spinner:
            self.spinner = st.spinner(f"⏳ {self.operation_name}...")
            self.spinner.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.spinner:
            self.spinner.__exit__(exc_type, exc_value, exc_traceback)
        
        if exc_type is not None:
            ui_logger.error(f"Error in {self.operation_name}: {exc_value}")
            display_error(f"❌ {self.operation_name} failed: {str(exc_value)}")
            return True  # Suppress the exception
        
        return False
