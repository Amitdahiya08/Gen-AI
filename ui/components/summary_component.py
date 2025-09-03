import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

def render():
    st.header("Document Summary")

    # Check if there's a current document
    if "current_doc_id" in st.session_state:
        doc_id = st.session_state.current_doc_id
        filename = st.session_state.current_doc_filename

        st.info(f"📄 Current Document: **{filename}** (ID: `{doc_id}`)")

        # Option to manually enter a different document ID
        with st.expander("🔄 Use Different Document"):
            manual_doc_id = st.text_input("Enter Document ID", key="summary_manual_doc_id")
            if st.button("Switch Document", key="summary_switch_button") and manual_doc_id:
                doc_id = manual_doc_id

        # Get Summary button or auto-load for current document
        load_summary = st.button("Get Summary", key="summary_get_button")

        # Auto-load summary if current document exists and no manual override
        if not load_summary and "current_doc_summary" in st.session_state and doc_id == st.session_state.current_doc_id:
            load_summary = True

        if load_summary:
            if "current_doc_summary" in st.session_state and doc_id == st.session_state.current_doc_id:
                # Use cached summary for current document
                summary_data = st.session_state.current_doc_summary
                st.success("✅ Using cached summary")
            else:
                # Fetch summary from backend
                response = requests.get(f"{BACKEND_URL}/summary/{doc_id}")
                if response.status_code == 200:
                    data = response.json()
                    summary_data = data["summary"]
                    # Cache the fetched summary
                    if doc_id == st.session_state.get("current_doc_id"):
                        st.session_state.current_doc_summary = summary_data
                else:
                    st.error("Document not found")
                    return

            # Create a unique key for the text area that includes doc_id to force refresh
            text_area_key = f"summary_text_area_{doc_id}"
            summary_text = st.text_area("Summary", value=summary_data, height=200, key=text_area_key)

            if st.button("Save Updated Summary", key="summary_save_button"):
                update_resp = requests.post(
                    f"{BACKEND_URL}/summary/{doc_id}/update",
                    json={"updated_summary": summary_text},
                )
                if update_resp.status_code == 200:
                    st.success("✅ Summary updated successfully!")
                    # Update session state if this is the current document
                    if doc_id == st.session_state.get("current_doc_id"):
                        st.session_state.current_doc_summary = summary_text
                    # Force a rerun to refresh the display
                    st.rerun()
                else:
                    st.error("❌ Update failed")
    else:
        st.warning("⚠️ No document uploaded yet. Please upload a document first in the Upload tab.")
