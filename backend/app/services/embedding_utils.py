"""
Embedding utilities for storing and retrieving embeddings from the database.
"""
import numpy as np
from typing import Optional, List, Union
import logging

logger = logging.getLogger(__name__)


def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    """
    Convert numpy embedding array to bytes for database storage.
    
    Args:
        embedding: Numpy array of embedding values
        
    Returns:
        Bytes representation of the embedding
    """
    if embedding is None:
        return None
    return embedding.astype(np.float32).tobytes()


def bytes_to_embedding(data: bytes, dim: int = 768) -> Optional[np.ndarray]:
    """
    Convert bytes back to numpy embedding array.
    
    Args:
        data: Bytes data from database
        dim: Expected dimension of embedding (768 for mpnet, 384 for minilm)
        
    Returns:
        Numpy array of embedding values
    """
    if data is None:
        return None
    try:
        return np.frombuffer(data, dtype=np.float32)
    except Exception as e:
        logger.error(f"Error converting bytes to embedding: {e}")
        return None


def compute_and_store_embedding(
    text: str,
    db_object,
    similarity_engine,
    force: bool = False
) -> np.ndarray:
    """
    Compute embedding for text and store it in the database object.
    
    Args:
        text: Text to embed
        db_object: SQLAlchemy model object with 'embedding' and 'embedding_model' columns
        similarity_engine: SimilarityEngine instance
        force: Recompute even if embedding exists
        
    Returns:
        The embedding array
    """
    # Check if embedding already exists
    if not force and db_object.embedding is not None:
        return bytes_to_embedding(db_object.embedding)
    
    # Compute embedding
    embedding = similarity_engine.get_embedding(text)
    
    # Store in database object
    db_object.embedding = embedding_to_bytes(embedding)
    db_object.embedding_model = similarity_engine._model_name
    
    return embedding


def batch_compute_embeddings(
    texts: List[str],
    similarity_engine
) -> List[np.ndarray]:
    """
    Compute embeddings for multiple texts efficiently.
    
    Args:
        texts: List of texts to embed
        similarity_engine: SimilarityEngine instance
        
    Returns:
        List of embedding arrays
    """
    return [similarity_engine.get_embedding(t) for t in texts]


def find_similar_by_embedding(
    query_embedding: np.ndarray,
    candidate_embeddings: List[np.ndarray],
    top_k: int = 10
) -> List[tuple]:
    """
    Find most similar items by comparing embeddings.
    
    Args:
        query_embedding: Query embedding vector
        candidate_embeddings: List of candidate embedding vectors
        top_k: Number of top results to return
        
    Returns:
        List of (index, similarity_score) tuples
    """
    from sklearn.metrics.pairwise import cosine_similarity
    
    if not candidate_embeddings:
        return []
    
    # Stack embeddings into matrix
    candidates_matrix = np.vstack(candidate_embeddings)
    query_matrix = query_embedding.reshape(1, -1)
    
    # Compute similarities
    similarities = cosine_similarity(query_matrix, candidates_matrix)[0]
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    return [(int(idx), float(similarities[idx])) for idx in top_indices]
