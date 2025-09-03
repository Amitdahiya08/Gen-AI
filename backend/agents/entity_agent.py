"""
Entity extraction agent for identifying and validating entities in text.

This module provides the EntityAgent class which extracts named entities
(names, dates, organizations) from text using regex patterns and validates
them using Azure OpenAI language models.
"""
import re
from typing import List, Dict
from backend.config import Config
import requests
from backend.utils.helpers import log_agent_action


class EntityAgent:
    """
    Named entity extraction and validation agent.

    This agent identifies and extracts named entities from text documents,
    including person names, dates, and organizations. It uses regex patterns
    for initial extraction and can validate results using Azure OpenAI.

    The agent extracts:
        - Names: Person names in "First Last" format
        - Dates: Dates in various formats (MM/DD/YYYY, MM-DD-YYYY, etc.)
        - Organizations: Companies, universities, and institutions

    Attributes:
        None (stateless agent)

    Example:
        >>> entity_agent = EntityAgent()
        >>> entities = entity_agent.extract("John Smith works at Microsoft Corp.")
        >>> print(entities)
        {'names': ['John Smith'], 'dates': [], 'organizations': ['Microsoft Corp']}
    """

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the given text.

        Uses regex patterns to identify and extract different types of entities
        from the input text. The extraction is rule-based and may not catch
        all possible entity variations, but provides a good baseline for
        common entity formats.

        Args:
            text (str): The text from which to extract entities

        Returns:
            Dict[str, List[str]]: Dictionary containing lists of extracted entities:
                - 'names': List of person names found
                - 'dates': List of dates found
                - 'organizations': List of organizations found

        Example:
            >>> agent = EntityAgent()
            >>> text = "John Doe met with Microsoft Corp on 12/25/2023."
            >>> entities = agent.extract(text)
            >>> print(entities['names'])
            ['John Doe']
            >>> print(entities['organizations'])
            ['Microsoft Corp']
            >>> print(entities['dates'])
            ['12/25/2023']
        """
        # Extract person names (First Last format)
        names = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text)

        # Extract dates in various formats (MM/DD/YYYY, MM-DD-YYYY, etc.)
        dates = re.findall(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", text)

        # Extract organizations (companies, universities, etc.)
        orgs = re.findall(r"\b[A-Z][A-Za-z]+(?: Corp| Inc| Ltd| University)\b", text)

        # Create entity dictionary with unique values
        entities = {
            "names": list(set(names)),
            "dates": list(set(dates)),
            "organizations": list(set(orgs)),
        }

        # Log the extraction for observability
        log_agent_action("EntityAgent", "extract", str(entities))
        return entities

    def validate_entities(self, text: str, entities: Dict[str, List[str]]) -> str:
        """
        Validate extracted entities using Azure OpenAI language model.

        This method sends the original text and extracted entities to an LLM
        for validation, checking if the entities are correctly identified and
        relevant to the context. This helps improve the accuracy of entity
        extraction by leveraging the language model's understanding.

        Args:
            text (str): The original text from which entities were extracted
            entities (Dict[str, List[str]]): The extracted entities to validate

        Returns:
            str: Validation result from the language model, or error message

        Example:
            >>> agent = EntityAgent()
            >>> text = "John Smith works at Microsoft Corp."
            >>> entities = {"names": ["John Smith"], "organizations": ["Microsoft Corp"], "dates": []}
            >>> validation = agent.validate_entities(text, entities)
            >>> print(validation)
            "The entities are correctly identified..."

        Note:
            - Text is truncated to 3000 characters to stay within token limits
            - Validation response is limited to 200 tokens for conciseness
            - All validation attempts are logged for observability
        """
        headers = {
            "Content-Type": "application/json",
            "api-key": Config.AZURE_OPENAI_API_KEY,
        }

        # Prepare the validation request
        body = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an entity validation assistant. Check if the extracted entities are correct and relevant to the given text."
                },
                {
                    "role": "user",
                    "content": f"Check if these entities are correct for the text:\n{text[:3000]}\nEntities: {entities}"
                }
            ],
            "max_tokens": 200,  # Limit response length
        }

        try:
            resp = requests.post(
                f"{Config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{Config.AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2024-05-01-preview",
                headers=headers,
                json=body,
                timeout=30  # Add timeout for reliability
            )

            if resp.status_code == 200:
                validation = resp.json()["choices"][0]["message"]["content"].strip()
                log_agent_action("EntityAgent", "validate_entities", validation[:200])
                return validation
            else:
                return f"Entity validation failed: HTTP {resp.status_code}"

        except requests.exceptions.RequestException as e:
            return f"Entity validation failed due to network error: {str(e)}"
        except Exception as e:
            return f"Entity validation failed due to unexpected error: {str(e)}"
