"""
Semantic Similarity Engine for Resume-Job Matching
Uses Sentence Transformers as the primary method for semantic similarity.
Models are cached in ~/.cache/torch/sentence_transformers/
"""
import os
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

# Set cache directory for sentence transformers (uses HuggingFace cache by default)
CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache', 'sentence_transformers')
os.makedirs(CACHE_DIR, exist_ok=True)

# Check for Sentence Transformers (primary method)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

# Import our consolidated NLP service
from .nlp_service import nlp_service


class SimilarityEngine:
    """
    Semantic similarity engine optimized for resume-job matching.
    
    Primary method: Sentence Transformers (all-mpnet-base-v2)
    Fallback: TF-IDF with cosine similarity
    
    Models are cached automatically - first load downloads, subsequent loads are instant.
    
    Usage:
        engine = SimilarityEngine()
        score = engine.calculate_similarity("resume text", "job description")
        embedding = engine.get_embedding("text to embed")
    """
    
    # Class-level model to share across instances
    _sentence_model = None
    _model_loading = False
    _model_failed = False
    _model_name = "all-mpnet-base-v2"  # Best quality model
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the similarity engine.
        
        Args:
            model_name: Sentence Transformer model to use. 
                       Options: 'all-mpnet-base-v2' (best), 'all-MiniLM-L6-v2' (faster)
        """
        if model_name:
            SimilarityEngine._model_name = model_name
        
        # Embedding cache to avoid recomputing
        self._cache: Dict[str, np.ndarray] = {}
        self._max_cache_size = 1000
        
        # TF-IDF fallback vectorizer
        self._tfidf_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        
        logger.info(f"SimilarityEngine initialized with model: {SimilarityEngine._model_name}")
    
    def _load_model(self):
        """Lazy load the Sentence Transformer model (cached after first download)"""
        if SimilarityEngine._sentence_model is not None:
            return
        if SimilarityEngine._model_loading or SimilarityEngine._model_failed:
            return
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            SimilarityEngine._model_failed = True
            return
        
        SimilarityEngine._model_loading = True
        try:
            # Check if model is already cached
            model_cache_path = os.path.join(CACHE_DIR, SimilarityEngine._model_name.replace('/', '_'))
            if os.path.exists(model_cache_path):
                logger.info(f"Loading cached model: {SimilarityEngine._model_name}")
            else:
                logger.info(f"Downloading model (one-time): {SimilarityEngine._model_name}")
            
            SimilarityEngine._sentence_model = SentenceTransformer(
                SimilarityEngine._model_name,
                cache_folder=CACHE_DIR
            )
            logger.info("Sentence Transformer model ready")
        except Exception as e:
            logger.error(f"Failed to load Sentence Transformer: {e}")
            SimilarityEngine._model_failed = True
        finally:
            SimilarityEngine._model_loading = False
    
    @property
    def model(self) -> Optional[SentenceTransformer]:
        """Get the loaded model, loading if necessary"""
        self._load_model()
        return SimilarityEngine._sentence_model
    
    @property
    def is_semantic_available(self) -> bool:
        """Check if semantic similarity is available"""
        return self.model is not None
    
    # ==================== CORE METHODS ====================
    
    def get_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Get the embedding vector for a text.
        
        Args:
            text: Text to embed
            use_cache: Whether to use/store in cache
            
        Returns:
            Embedding vector (numpy array)
        """
        if not text:
            # Return zero vector of expected dimension
            dim = 768 if SimilarityEngine._model_name == "all-mpnet-base-v2" else 384
            return np.zeros(dim)
        
        # Check cache
        cache_key = hash(text)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Clean text
        cleaned_text = nlp_service.clean_text(text)
        
        # Get embedding
        if self.model:
            embedding = self.model.encode(cleaned_text, convert_to_numpy=True)
        else:
            # Fallback: TF-IDF sparse vector (less meaningful but better than nothing)
            embedding = self._get_tfidf_embedding(cleaned_text)
        
        # Cache result
        if use_cache:
            self._add_to_cache(cache_key, embedding)
        
        return embedding
    
    def get_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> np.ndarray:
        """
        Get embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use/store in cache
            
        Returns:
            Array of embeddings (n_texts x embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Clean texts
        cleaned_texts = [nlp_service.clean_text(t) for t in texts]
        
        if self.model:
            embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True, show_progress_bar=False)
        else:
            embeddings = np.array([self._get_tfidf_embedding(t) for t in cleaned_texts])
        
        # Cache results
        if use_cache:
            for text, emb in zip(texts, embeddings):
                self._add_to_cache(hash(text), emb)
        
        return embeddings
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            emb1 = self.get_embedding(text1)
            emb2 = self.get_embedding(text2)
            
            # Cosine similarity
            similarity = cosine_similarity(
                emb1.reshape(1, -1), 
                emb2.reshape(1, -1)
            )[0][0]
            
            # Ensure in valid range
            return float(max(0.0, min(1.0, similarity)))
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return self._calculate_tfidf_similarity(text1, text2)
    
    def calculate_similarity_batch(self, 
                                   query: str, 
                                   candidates: List[str]) -> List[float]:
        """
        Calculate similarity of a query against multiple candidates.
        
        Args:
            query: Query text (e.g., job description)
            candidates: List of candidate texts (e.g., resumes)
            
        Returns:
            List of similarity scores
        """
        if not query or not candidates:
            return [0.0] * len(candidates)
        
        try:
            # Get embeddings
            query_emb = self.get_embedding(query).reshape(1, -1)
            candidate_embs = self.get_embeddings_batch(candidates)
            
            # Calculate all similarities at once
            similarities = cosine_similarity(query_emb, candidate_embs)[0]
            
            return [float(max(0.0, min(1.0, s))) for s in similarities]
            
        except Exception as e:
            logger.error(f"Error in batch similarity: {e}")
            return [self._calculate_tfidf_similarity(query, c) for c in candidates]
    
    def find_most_similar(self, 
                          query: str, 
                          candidates: List[str], 
                          top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Find the most similar candidates to a query.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of (index, score) tuples, sorted by score descending
        """
        similarities = self.calculate_similarity_batch(query, candidates)
        
        # Create (index, score) pairs and sort
        indexed = list(enumerate(similarities))
        indexed.sort(key=lambda x: x[1], reverse=True)
        
        return indexed[:top_k]
    
    # ==================== SKILL MATCHING ====================
    
    def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate similarity between two skills using embeddings.
        Handles skill variations like "React" vs "React.js" vs "ReactJS"
        """
        return self.calculate_similarity(skill1, skill2)
    
    def match_skills_semantic(self, 
                              resume_skills: List[str], 
                              job_skills: List[str],
                              threshold: float = 0.7) -> Dict[str, any]:
        """
        Match skills semantically using embeddings.
        
        Args:
            resume_skills: Skills from resume
            job_skills: Required skills from job
            threshold: Minimum similarity to consider a match
            
        Returns:
            Dict with matched_skills, missing_skills, and match_details
        """
        if not job_skills:
            return {
                "matched_skills": resume_skills,
                "missing_skills": [],
                "match_details": {},
                "match_score": 1.0
            }
        
        if not resume_skills:
            return {
                "matched_skills": [],
                "missing_skills": job_skills,
                "match_details": {},
                "match_score": 0.0
            }
        
        # Get embeddings
        resume_embs = self.get_embeddings_batch(resume_skills)
        job_embs = self.get_embeddings_batch(job_skills)
        
        # Calculate similarity matrix
        sim_matrix = cosine_similarity(job_embs, resume_embs)
        
        matched_skills = []
        missing_skills = []
        match_details = {}
        
        for i, job_skill in enumerate(job_skills):
            best_match_idx = np.argmax(sim_matrix[i])
            best_score = sim_matrix[i][best_match_idx]
            
            if best_score >= threshold:
                matched_resume_skill = resume_skills[best_match_idx]
                matched_skills.append(job_skill)
                match_details[job_skill] = {
                    "matched_with": matched_resume_skill,
                    "similarity": float(best_score)
                }
            else:
                missing_skills.append(job_skill)
                match_details[job_skill] = {
                    "best_candidate": resume_skills[best_match_idx] if resume_skills else None,
                    "similarity": float(best_score)
                }
        
        match_score = len(matched_skills) / len(job_skills)
        
        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_details": match_details,
            "match_score": match_score
        }
    
    # ==================== FALLBACK METHODS ====================
    
    def _get_tfidf_embedding(self, text: str) -> np.ndarray:
        """Get a TF-IDF based embedding as fallback"""
        try:
            # Fit on single text and get vector
            tfidf_matrix = self._tfidf_vectorizer.fit_transform([text])
            return tfidf_matrix.toarray().flatten()
        except Exception:
            return np.zeros(5000)
    
    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF cosine similarity as fallback"""
        if not text1 or not text2:
            return 0.0
        
        try:
            cleaned1 = nlp_service.clean_text(text1)
            cleaned2 = nlp_service.clean_text(text2)
            
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform([cleaned1, cleaned2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.error(f"TF-IDF similarity error: {e}")
            return 0.0
    
    # ==================== CACHE MANAGEMENT ====================
    
    def _add_to_cache(self, key: int, value: np.ndarray):
        """Add embedding to cache with size limit"""
        if len(self._cache) >= self._max_cache_size:
            # Remove oldest entry (first key)
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = value
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self._cache.clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self._max_cache_size
        }
    
    # ==================== LEGACY COMPATIBILITY ====================
    # These methods maintain backward compatibility with existing code
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Alias for calculate_similarity (backward compatibility)"""
        return self.calculate_similarity(text1, text2)
    
    def calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF similarity (backward compatibility)"""
        return self._calculate_tfidf_similarity(text1, text2)
    
    def calculate_sentence_transformer_similarity(self, text1: str, text2: str) -> float:
        """Calculate using Sentence Transformers (backward compatibility)"""
        return self.calculate_similarity(text1, text2)
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text (backward compatibility)"""
        return nlp_service.clean_text(text)
    
    def batch_similarity_calculation(self, texts: List[str], reference_text: str) -> List[float]:
        """Calculate batch similarities (backward compatibility)"""
        return self.calculate_similarity_batch(reference_text, texts)


# Create default instance for easy import
similarity_engine = SimilarityEngine()
