"""
Question-answering agent for document-based Q&A using Azure OpenAI.

This module provides the QAAgent class which answers questions based on
document content using Azure OpenAI language models for accurate,
context-aware responses.
"""
from backend.config import Config
import requests
from backend.utils.helpers import log_agent_action


class QAAgent:
    """
    Question-answering agent for document-based queries.

    This agent provides intelligent question-answering capabilities over
    document content using Azure OpenAI language models. It ensures that
    answers are grounded in the provided document content and handles
    various edge cases gracefully.

    Features:
        - Document-grounded Q&A: Answers are based only on provided content
        - Input validation: Handles empty questions and documents
        - Error handling: Graceful handling of API failures
        - Logging: All Q&A interactions are logged for observability

    Attributes:
        None (stateless agent)

    Example:
        >>> qa_agent = QAAgent()
        >>> answer = qa_agent.ask("What is this document about?", document_text)
        >>> print(answer)
    """

    def ask(self, question: str, doc_text: str) -> str:
        """
        Answer a question based on the provided document content.

        This method takes a user question and document text, then uses
        Azure OpenAI to generate an accurate answer based solely on the
        document content. The response is grounded in the provided text
        to ensure factual accuracy.

        Args:
            question (str): The question to answer
            doc_text (str): The document content to base the answer on

        Returns:
            str: The answer to the question based on the document content,
                 or an appropriate error message if the operation fails

        Example:
            >>> qa_agent = QAAgent()
            >>> doc = "This document discusses machine learning algorithms..."
            >>> question = "What does this document discuss?"
            >>> answer = qa_agent.ask(question, doc)
            >>> print(answer)
            "This document discusses machine learning algorithms..."

        Note:
            - Questions and documents are validated before processing
            - Document text is truncated to 4000 characters for token limits
            - Responses are limited to 300 tokens for conciseness
            - All interactions are logged for monitoring and debugging
        """
        # Validate inputs
        if not question.strip():
            return "No question provided."
        if not doc_text.strip():
            return "No document content available."

        # Prepare API request
        headers = {
            "Content-Type": "application/json",
            "api-key": Config.AZURE_OPENAI_API_KEY,
        }

        body = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Q&A assistant. Answer based only on the provided document. If the answer is not in the document, say so clearly."
                },
                {
                    "role": "user",
                    "content": f"Document:\n{doc_text[:4000]}\n\nQuestion: {question}"
                }
            ],
            "max_tokens": 300,  # Limit response length
        }

        try:
            resp = requests.post(
                f"{Config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{Config.AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2024-05-01-preview",
                headers=headers,
                json=body,
                timeout=30  # Add timeout for reliability
            )

            if resp.status_code == 200:
                ans = resp.json()["choices"][0]["message"]["content"].strip()

                # Log the Q&A interaction
                log_agent_action("QAAgent", "ask", f"Q: {question[:100]} | A: {ans[:200]}")

                return ans if ans else "No relevant answer found."
            else:
                return f"Q&A failed: HTTP {resp.status_code} - {resp.text}"

        except requests.exceptions.RequestException as e:
            return f"Q&A failed due to network error: {str(e)}"
        except Exception as e:
            return f"Q&A failed due to unexpected error: {str(e)}"
