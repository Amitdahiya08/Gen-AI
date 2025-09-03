import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

def render():
    st.header("Q&A History")

    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    if st.session_state.qa_history:
        st.write(f"📚 **{len(st.session_state.qa_history)}** questions asked")

        # Add clear history button
        if st.button("🗑️ Clear History", key="clear_history_button"):
            st.session_state.qa_history = []
            st.rerun()

        st.divider()

        # Display history in reverse order (newest first)
        for i, qa in enumerate(reversed(st.session_state.qa_history)):
            with st.expander(f"Q{len(st.session_state.qa_history)-i}: {qa['q'][:50]}..."):
                st.markdown(f"**📄 Document:** {qa.get('filename', 'Unknown')} (`{qa.get('doc_id', 'N/A')}`)")
                st.markdown(f"**❓ Question:** {qa['q']}")
                st.markdown(f"**💡 Answer:** {qa['a']}")
                st.divider()
    else:
        st.info("🤔 No questions asked yet. Go to the Q&A tab to start asking questions!")
