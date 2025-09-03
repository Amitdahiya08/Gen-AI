"""
Document upload component with comprehensive error handling.

This component handles file uploads, processes them through the backend API,
and displays results with proper error handling and user feedback.
"""
import streamlit as st
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from error_handler import (
    safe_api_call,
    handle_api_error,
    display_error,
    display_success,
    handle_file_upload_error,
    SafeOperation,
    log_user_action
)

BACKEND_URL = "http://localhost:8000"


@safe_api_call
def upload_document_to_backend(uploaded_file):
    """
    Upload document to backend API with error handling.

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        dict: API response data or None if error
    """
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    response = requests.post(f"{BACKEND_URL}/documents/upload", files=files, timeout=30)

    if response.status_code == 200:
        return response.json()
    else:
        error_message = handle_api_error(response)
        display_error(error_message)
        return None


def validate_uploaded_file(uploaded_file) -> bool:
    """
    Validate uploaded file before processing.

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        bool: True if file is valid, False otherwise
    """
    if not uploaded_file:
        return False

    # Check file size (10MB limit)
    if uploaded_file.size > 10 * 1024 * 1024:
        display_error("📁 File Too Large: Please upload a file smaller than 10MB")
        return False

    # Check file type
    allowed_types = ["pdf", "docx", "html"]
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension not in allowed_types:
        display_error(f"📄 Invalid File Type: Please upload a {', '.join(allowed_types).upper()} file")
        return False

    return True


def display_upload_results(data: dict, filename: str):
    """
    Display upload results in a user-friendly format.

    Args:
        data: API response data
        filename: Name of uploaded file
    """
    display_success(f"✅ Successfully uploaded: {filename}")

    # Document info
    st.info(f"📄 **Document ID:** `{data['doc_id']}`")

    # Summary section
    st.subheader("📋 Generated Summary")
    summary = data.get("summary", "No summary available")

    if "rolled back" in summary.lower():
        st.warning("⚠️ Summary Quality Warning")
        st.write(summary)
    else:
        st.write(summary)

    # Entities section
    st.subheader("🏷️ Extracted Entities")
    entities = data.get("entities", {})

    if "error" in entities:
        st.warning("⚠️ Entity Extraction Warning")
        st.write(entities["error"])
    else:
        # Display entities in a more user-friendly format
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**👤 Names:**")
            names = entities.get("names", [])
            if names:
                for name in names:
                    st.write(f"• {name}")
            else:
                st.write("_None found_")

        with col2:
            st.write("**📅 Dates:**")
            dates = entities.get("dates", [])
            if dates:
                for date in dates:
                    st.write(f"• {date}")
            else:
                st.write("_None found_")

        with col3:
            st.write("**🏢 Organizations:**")
            orgs = entities.get("organizations", [])
            if orgs:
                for org in orgs:
                    st.write(f"• {org}")
            else:
                st.write("_None found_")


def render():
    """Render the document upload component with comprehensive error handling."""
    st.header("📤 Upload Document")

    # Instructions
    st.write("Upload a PDF, DOCX, or HTML document to get started with AI-powered analysis.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "html"],
        key="upload_file_uploader",
        help="Supported formats: PDF, DOCX, HTML (Max size: 10MB)"
    )

    if uploaded_file:
        log_user_action("file_selected", f"File: {uploaded_file.name}, Size: {uploaded_file.size} bytes")

        # Validate file
        if not validate_uploaded_file(uploaded_file):
            return

        # Show file info
        st.write(f"**Selected file:** {uploaded_file.name}")
        st.write(f"**File size:** {uploaded_file.size / 1024:.1f} KB")
        st.write(f"**File type:** {uploaded_file.type}")

        # Upload button
        if st.button("🚀 Process Document", type="primary"):
            log_user_action("upload_initiated", uploaded_file.name)

            try:
                with SafeOperation("Processing document", show_spinner=True):
                    # Upload to backend
                    data = upload_document_to_backend(uploaded_file)

                    if data:
                        # Store the current document info in session state
                        st.session_state.current_doc_id = data["doc_id"]
                        st.session_state.current_doc_filename = data["filename"]
                        st.session_state.current_doc_summary = data["summary"]
                        st.session_state.current_doc_entities = data["entities"]

                        # Display results
                        display_upload_results(data, uploaded_file.name)

                        log_user_action("upload_completed", f"Doc ID: {data['doc_id']}")

                        # Show next steps
                        st.info("🎯 **Next Steps:** Use the Summary tab to edit the summary, or go to Q&A to ask questions about your document.")

            except Exception as e:
                error_message = handle_file_upload_error(e)
                display_error(error_message)
                log_user_action("upload_failed", f"Error: {str(e)}")

    else:
        # Show upload tips when no file is selected
        with st.expander("💡 Upload Tips"):
            st.write("""
            **Supported file formats:**
            - 📄 **PDF**: Text-based PDFs work best (scanned images may have limited accuracy)
            - 📝 **DOCX**: Microsoft Word documents
            - 🌐 **HTML**: Web pages and HTML documents

            **Best practices:**
            - Keep files under 10MB for optimal performance
            - Ensure text is clearly readable
            - Avoid password-protected files
            """)

        # Show sample documents or recent uploads
        if "recent_uploads" in st.session_state and st.session_state.recent_uploads:
            st.subheader("📚 Recent Uploads")
            for doc_id, filename in st.session_state.recent_uploads[-3:]:
                if st.button(f"📄 {filename}", key=f"recent_{doc_id}"):
                    st.session_state.current_doc_id = doc_id
                    st.session_state.current_doc_filename = filename
                    st.success(f"✅ Switched to: {filename}")
                    st.rerun()
