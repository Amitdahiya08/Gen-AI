"""
Utility functions for the Streamlit UI
"""
import streamlit as st

def get_current_document():
    """Get the current active document from session state"""
    if "current_doc_id" in st.session_state:
        return {
            "doc_id": st.session_state.current_doc_id,
            "filename": st.session_state.current_doc_filename,
            "summary": st.session_state.get("current_doc_summary", ""),
            "entities": st.session_state.get("current_doc_entities", {})
        }
    return None

def set_current_document(doc_id, filename, summary=None, entities=None):
    """Set the current active document in session state"""
    st.session_state.current_doc_id = doc_id
    st.session_state.current_doc_filename = filename
    if summary:
        st.session_state.current_doc_summary = summary
    if entities:
        st.session_state.current_doc_entities = entities

def clear_current_document():
    """Clear the current active document from session state"""
    keys_to_remove = [
        "current_doc_id", 
        "current_doc_filename", 
        "current_doc_summary", 
        "current_doc_entities"
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def has_current_document():
    """Check if there's a current active document"""
    return "current_doc_id" in st.session_state
