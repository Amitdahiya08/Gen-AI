import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

def render():
    st.header("Ask Questions about Document")

    # Check if there's a current document
    if "current_doc_id" in st.session_state:
        doc_id = st.session_state.current_doc_id
        filename = st.session_state.current_doc_filename

        st.info(f"📄 Current Document: **{filename}** (ID: `{doc_id}`)")

        # Option to manually enter a different document ID
        with st.expander("🔄 Use Different Document"):
            manual_doc_id = st.text_input("Enter Document ID", key="qa_manual_doc_id")
            if st.button("Switch Document", key="qa_switch_button") and manual_doc_id:
                doc_id = manual_doc_id

        question = st.text_input("Enter your question", key="qa_question")
        if st.button("Ask", key="qa_ask_button"):
            if question:
                response = requests.get(f"{BACKEND_URL}/qa/", params={"doc_id": doc_id, "question": question})
                if response.status_code == 200:
                    data = response.json()
                    answer = data['answer']
                    st.success(f"**Answer:** {answer}")

                    # Save to history
                    if "qa_history" not in st.session_state:
                        st.session_state.qa_history = []

                    st.session_state.qa_history.append({
                        "q": question,
                        "a": answer,
                        "doc_id": doc_id,
                        "filename": filename
                    })
                else:
                    st.error("Failed to get answer")
            else:
                st.warning("Please enter a question first.")
    else:
        st.warning("⚠️ No document uploaded yet. Please upload a document first in the Upload tab.")
