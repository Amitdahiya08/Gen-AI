import streamlit as st
import json
import sys
import os

# Add the parent directory to the Python path to access backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.routes.documents import documents_store

def render():
    st.header("Export Summaries & Entities")
    if documents_store:
        export_data = {
            doc_id: {"summary": doc["summary"], "entities": doc["entities"]}
            for doc_id, doc in documents_store.items()
        }
        st.download_button(
            label="Download Export (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name="summaries_entities.json",
            mime="application/json",
            key="export_download_button"
        )
    else:
        st.info("No documents available to export")
