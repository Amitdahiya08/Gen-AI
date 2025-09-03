"""
Embedding service for vector operations and semantic search.

This module provides text embedding functionality using sentence-transformers
for vector database operations and semantic similarity search.
"""
import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import Config

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and managing text embeddings.
    
    This service uses sentence-transformers to generate vector embeddings
    for text chunks, enabling semantic search and similarity operations.
    """
    
    def __init__(self):
        """Initialize the embedding service with the configured model."""
        self.model_name = Config.EMBEDDING_MODEL
        self.dimension = Config.VECTOR_DIMENSION
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model {self.model_name}: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List[float]: Embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        if not self.model:
            raise Exception("Embedding model not loaded")
        
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.dimension
        
        try:
            # Generate embedding
            embedding = self.model.encode(text.strip())
            
            # Ensure correct dimension
            if len(embedding) != self.dimension:
                logger.warning(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}")
            
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batch processing).
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
            
        Raises:
            Exception: If embedding generation fails
        """
        if not self.model:
            raise Exception("Embedding model not loaded")
        
        if not texts:
            return []
        
        try:
            # Filter out empty texts and keep track of indices
            valid_texts = []
            valid_indices = []
            
            for i, text in enumerate(texts):
                if text and text.strip():
                    valid_texts.append(text.strip())
                    valid_indices.append(i)
            
            if not valid_texts:
                # Return zero vectors for all texts
                return [[0.0] * self.dimension] * len(texts)
            
            # Generate embeddings for valid texts
            embeddings = self.model.encode(valid_texts)
            
            # Create result list with zero vectors for empty texts
            result = []
            valid_idx = 0
            
            for i in range(len(texts)):
                if i in valid_indices:
                    embedding = embeddings[valid_idx]
                    result.append(embedding.tolist())
                    valid_idx += 1
                else:
                    result.append([0.0] * self.dimension)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings for {len(texts)} texts: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for embedding.
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this is not the last chunk, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary (. ! ?)
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Cosine similarity score (0-1)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_most_similar_chunks(
        self, 
        query_embedding: List[float], 
        chunk_embeddings: List[List[float]], 
        chunk_texts: List[str],
        top_k: int = 3
    ) -> List[tuple]:
        """
        Find the most similar text chunks to a query embedding.
        
        Args:
            query_embedding: Query embedding vector
            chunk_embeddings: List of chunk embedding vectors
            chunk_texts: List of corresponding chunk texts
            top_k: Number of top results to return
            
        Returns:
            List[tuple]: List of (chunk_text, similarity_score) tuples
        """
        if not chunk_embeddings or not chunk_texts:
            return []
        
        if len(chunk_embeddings) != len(chunk_texts):
            logger.error("Mismatch between embeddings and texts length")
            return []
        
        try:
            similarities = []
            
            for i, chunk_embedding in enumerate(chunk_embeddings):
                similarity = self.calculate_similarity(query_embedding, chunk_embedding)
                similarities.append((chunk_texts[i], similarity, i))
            
            # Sort by similarity (descending) and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return [(text, score) for text, score, _ in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Failed to find similar chunks: {e}")
            return []
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded embedding model.
        
        Returns:
            dict: Model information
        """
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "is_loaded": self.model is not None,
            "max_seq_length": getattr(self.model, 'max_seq_length', None) if self.model else None
        }
