"""
Main Streamlit application with global error handling.

This is the entry point for the document summarization and Q&A platform UI,
featuring comprehensive error handling and user-friendly error display.
"""
import streamlit as st
from components import upload_component, summary_component, qa_component, monitor_component, history_component, export_component
from error_handler import create_error_boundary, display_global_error, safe_streamlit_component, log_user_action

# Configure Streamlit page
st.set_page_config(
    page_title="Doc Summarization & Q&A",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize global error handling
create_error_boundary()

# Display any global errors
display_global_error()


@safe_streamlit_component
def render_header():
    """Render the application header with current document status."""
    st.title("📄 Intelligent Document Summarization & Q&A Platform")

    # Show current document status at the top
    if "current_doc_id" in st.session_state:
        st.info(f"🎯 **Active Document:** {st.session_state.current_doc_filename} | **ID:** `{st.session_state.current_doc_id}`")
        log_user_action("view_header", f"Active document: {st.session_state.current_doc_filename}")
    else:
        st.warning("⚠️ No active document. Upload a document to get started!")


@safe_streamlit_component
def render_tabs():
    """Render the main application tabs with error handling."""
    tabs = st.tabs(["📤 Upload", "📋 Summary", "❓ Q&A", "📊 Monitor", "📚 History", "💾 Export"])

    with tabs[0]:
        log_user_action("navigate_to_tab", "Upload")
        upload_component.render()

    with tabs[1]:
        log_user_action("navigate_to_tab", "Summary")
        summary_component.render()

    with tabs[2]:
        log_user_action("navigate_to_tab", "Q&A")
        qa_component.render()

    with tabs[3]:
        log_user_action("navigate_to_tab", "Monitor")
        monitor_component.render()

    with tabs[4]:
        log_user_action("navigate_to_tab", "History")
        history_component.render()

    with tabs[5]:
        log_user_action("navigate_to_tab", "Export")
        export_component.render()


@safe_streamlit_component
def render_footer():
    """Render application footer with status information."""
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🤖 AI-Powered Document Processing")

    with col2:
        st.caption("📊 Real-time Analysis & Q&A")

    with col3:
        st.caption("🔒 Secure & Private")


def main():
    """Main application entry point with comprehensive error handling."""
    try:
        # Render main components
        render_header()
        render_tabs()
        render_footer()

        # Log successful app load
        if "app_loaded" not in st.session_state:
            st.session_state.app_loaded = True
            log_user_action("app_loaded", "Application successfully loaded")

    except Exception as e:
        # Catch any unhandled exceptions at the top level
        st.error("🚨 Application Error")
        st.write("An unexpected error occurred. Please refresh the page.")

        with st.expander("🔍 Error Details"):
            st.code(f"Error: {str(e)}")

        if st.button("🔄 Refresh Application"):
            st.rerun()


if __name__ == "__main__":
    main()
