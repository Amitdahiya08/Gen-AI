import streamlit as st
import sys
import os

# Add the parent directory to the Python path to access backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.routes.documents import documents_store

def render():
    st.header("Monitoring & Logs")

    # Show current document status
    if "current_doc_id" in st.session_state:
        current_doc_id = st.session_state.current_doc_id
        current_filename = st.session_state.current_doc_filename
        st.success(f"🎯 **Current Active Document:** {current_filename} (`{current_doc_id}`)")
    else:
        st.info("ℹ️ No active document selected")

    st.divider()
    st.subheader("All Stored Documents")

    if documents_store:
        for doc_id, doc in documents_store.items():
            # Highlight current document
            is_current = "current_doc_id" in st.session_state and doc_id == st.session_state.current_doc_id

            if is_current:
                st.markdown(f"🎯 **{doc['filename']}** (Current)")
            else:
                st.markdown(f"📄 **{doc['filename']}**")

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**ID:** `{doc_id}`")
                st.write(f"**Summary:** {doc['summary'][:200]}...")
                with st.expander("View Entities"):
                    st.json(doc['entities'])

            with col2:
                if not is_current:
                    if st.button(f"Set as Current", key=f"set_current_{doc_id}"):
                        st.session_state.current_doc_id = doc_id
                        st.session_state.current_doc_filename = doc['filename']
                        st.session_state.current_doc_summary = doc['summary']
                        st.session_state.current_doc_entities = doc['entities']
                        st.rerun()

            st.divider()
    else:
        st.info("No documents uploaded yet.")
