"""
Document summarization agent using Azure OpenAI.

This module provides the SummarizerAgent class which generates summaries at
different levels (section, document, corpus) using Azure OpenAI's language models.
"""
from backend.config import Config
import requests
from backend.utils.helpers import log_agent_action


class SummarizerAgent:
    """
    Document summarization agent using Azure OpenAI language models.

    This agent provides multi-level summarization capabilities including
    section-wise, document-level, and corpus-level summarization. It uses
    Azure OpenAI's GPT models to generate high-quality summaries with
    configurable parameters.

    The agent supports:
        - Section summarization: Summarize individual sections of text
        - Document summarization: Create section-wise summaries of entire documents
        - Corpus summarization: Generate summaries across multiple documents

    Attributes:
        system_prompt (str): The system prompt used for all LLM interactions

    Example:
        >>> summarizer = SummarizerAgent()
        >>> summary = summarizer.summarize_document("Long document text...")
        >>> print(summary)
    """

    def __init__(self):
        """
        Initialize the SummarizerAgent with default configuration.

        Sets up the system prompt that will be used for all summarization
        requests to ensure consistent behavior and output quality.
        """
        self.system_prompt = "You are a document summarization agent."

    def summarize_section(self, text: str) -> str:
        """
        Generate a summary for a specific section of text.

        This method is designed for summarizing individual sections or
        paragraphs of a larger document. It provides focused summaries
        that capture the key points of the given text section.

        Args:
            text (str): The text section to summarize

        Returns:
            str: A concise summary of the section

        Example:
            >>> summarizer = SummarizerAgent()
            >>> section_text = "This section discusses machine learning algorithms..."
            >>> summary = summarizer.summarize_section(section_text)
            >>> print(summary)
        """
        result = self._call_llm(f"Summarize this section:\n{text}")
        log_agent_action("SummarizerAgent", "summarize_section", result[:200])
        return result

    def summarize_document(self, text: str) -> str:
        """
        Generate a comprehensive summary of an entire document.

        This method creates a section-wise summary that breaks down the
        document into logical sections and provides summaries for each,
        giving readers a structured overview of the entire document.

        Args:
            text (str): The full document text to summarize

        Returns:
            str: A structured, section-wise summary of the document

        Example:
            >>> summarizer = SummarizerAgent()
            >>> doc_text = "Full document content with multiple sections..."
            >>> summary = summarizer.summarize_document(doc_text)
            >>> print(summary)
        """
        result = self._call_llm(f"Provide a section-wise summary of this document:\n{text}")
        log_agent_action("SummarizerAgent", "summarize_document", result[:200])
        return result

    def summarize_corpus(self, texts: list[str]) -> str:
        """
        Generate a summary across multiple documents (corpus-level).

        This method takes multiple document texts and creates a unified
        summary that identifies common themes, patterns, and key insights
        across the entire corpus of documents.

        Args:
            texts (list[str]): List of document texts to summarize together

        Returns:
            str: A unified summary across all provided documents

        Example:
            >>> summarizer = SummarizerAgent()
            >>> documents = ["Doc 1 text...", "Doc 2 text...", "Doc 3 text..."]
            >>> corpus_summary = summarizer.summarize_corpus(documents)
            >>> print(corpus_summary)
        """
        joined = "\n\n".join(texts)
        result = self._call_llm(f"Summarize across documents:\n{joined}")
        log_agent_action("SummarizerAgent", "summarize_corpus", result[:200])
        return result

    def _call_llm(self, user_content: str) -> str:
        """
        Make a call to Azure OpenAI language model for summarization.

        This private method handles the actual API communication with Azure OpenAI,
        including request formatting, error handling, and response processing.
        Content is automatically truncated to fit within token limits.

        Args:
            user_content (str): The content to send to the LLM for summarization

        Returns:
            str: The generated summary or an error message

        Note:
            - Content is truncated to 4000 characters to stay within token limits
            - Maximum response tokens is set to 500 for concise summaries
            - All API calls are logged for observability
            - Handles both successful responses and API errors gracefully
        """
        headers = {
            "Content-Type": "application/json",
            "api-key": Config.AZURE_OPENAI_API_KEY,
        }
        body = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_content[:4000]},  # Truncate to stay within limits
            ],
            "max_tokens": 500,  # Limit response length for concise summaries
        }

        try:
            resp = requests.post(
                f"{Config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{Config.AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2024-05-01-preview",
                headers=headers,
                json=body,
                timeout=30  # Add timeout for reliability
            )

            if resp.status_code == 200:
                output = resp.json()["choices"][0]["message"]["content"].strip()
                return output if output else "No summary generated."
            else:
                return f"Summarization failed: {resp.text}"

        except requests.exceptions.RequestException as e:
            return f"Summarization failed due to network error: {str(e)}"
        except Exception as e:
            return f"Summarization failed due to unexpected error: {str(e)}"
