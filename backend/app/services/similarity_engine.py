import numpy as np
from typing import List, Dict, Tuple, Optional
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
try:
    from transformers import BertTokenizer, BertModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: transformers not available. Using fallback similarity methods.")
    TRANSFORMERS_AVAILABLE = False
    BertTokenizer = None
    BertModel = None

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: torch not available. Using TF-IDF only.")
    TORCH_AVAILABLE = False
    torch = None
    F = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers not available. Using fallback similarity methods.")
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from .text_preprocessor import TextPreprocessor


class SimilarityEngine:
    """Advanced NLP-based similarity calculation engine for resumes and job descriptions"""

    def __init__(self, use_gpu: bool = False):
        self.text_preprocessor = TextPreprocessor()
        if TORCH_AVAILABLE:
            self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        else:
            self.device = None
        
        # Initialize TF-IDF vectorizer with optimized parameters
        self.tfidf_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=10000,
            ngram_range=(1, 2),  # Include bigrams for better context
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.8,  # Ignore terms that appear in more than 80% of documents
            sublinear_tf=True  # Use sublinear scaling for TF
        )
        
        # Initialize BERT model and tokenizer
        if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
            try:
                self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
                self.bert_model = BertModel.from_pretrained('bert-base-uncased')
                if self.device:
                    self.bert_model.to(self.device)
                self.bert_model.eval()
            except Exception as e:
                print(f"Warning: Could not load BERT model: {e}")
                self.bert_tokenizer = None
                self.bert_model = None
        else:
            self.bert_tokenizer = None
            self.bert_model = None
        
        # Initialize Sentence Transformer for better embeddings
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load Sentence Transformer: {e}")
                self.sentence_model = None
        else:
            self.sentence_model = None
        
        # Cache for embeddings to improve performance
        self.embedding_cache = {}
        self.max_cache_size = 1000
        
        # LSA for dimensionality reduction
        self.lsa = TruncatedSVD(n_components=100, random_state=42)
        self.lsa_fitted = False

    def _get_cache_key(self, text: str, method: str) -> str:
        """Generate cache key for embeddings"""
        return f"{method}_{hash(text)}"

    def _add_to_cache(self, key: str, value: np.ndarray):
        """Add embedding to cache with size limit"""
        if len(self.embedding_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.embedding_cache))
            del self.embedding_cache[oldest_key]
        
        self.embedding_cache[key] = value

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for similarity calculation"""
        # Basic cleaning
        cleaned_text = self.text_preprocessor.clean_text(text)
        
        # Additional preprocessing for similarity
        # Remove extra whitespace
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text

    def calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using TF-IDF vectorization and cosine similarity"""
        if not text1 or not text2:
            return 0.0
        
        # Preprocess texts
        processed_text1 = self.preprocess_text(text1)
        processed_text2 = self.preprocess_text(text2)
        
        try:
            # Fit and transform texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([processed_text1, processed_text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Error in TF-IDF similarity calculation: {e}")
            return 0.0

    def calculate_tfidf_similarity_batch(self, texts: List[str]) -> np.ndarray:
        """Calculate TF-IDF similarity matrix for multiple texts"""
        if not texts:
            return np.array([])
        
        # Preprocess all texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        try:
            # Fit and transform all texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
            
            # Calculate pairwise similarities
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            return similarity_matrix
        except Exception as e:
            print(f"Error in batch TF-IDF similarity calculation: {e}")
            return np.zeros((len(texts), len(texts)))

    def calculate_bert_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using BERT embeddings and cosine similarity"""
        if not self.bert_model or not self.bert_tokenizer:
            return 0.0
        
        if not text1 or not text2:
            return 0.0
        
        try:
            # Check cache first
            cache_key1 = self._get_cache_key(text1, 'bert')
            cache_key2 = self._get_cache_key(text2, 'bert')
            
            if cache_key1 in self.embedding_cache:
                embedding1 = self.embedding_cache[cache_key1]
            else:
                embedding1 = self._get_bert_embedding(text1)
                self._add_to_cache(cache_key1, embedding1)
            
            if cache_key2 in self.embedding_cache:
                embedding2 = self.embedding_cache[cache_key2]
            else:
                embedding2 = self._get_bert_embedding(text2)
                self._add_to_cache(cache_key2, embedding2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Error in BERT similarity calculation: {e}")
            return 0.0

    def _get_bert_embedding(self, text: str) -> np.ndarray:
        """Get BERT embedding for a single text"""
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Tokenize
        inputs = self.bert_tokenizer(
            processed_text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
            
            # Use mean pooling of last hidden state
            last_hidden_state = outputs.last_hidden_state
            attention_mask = inputs['attention_mask']
            
            # Apply attention mask and calculate mean
            masked_embeddings = last_hidden_state * attention_mask.unsqueeze(-1)
            summed_embeddings = torch.sum(masked_embeddings, dim=1)
            summed_mask = torch.sum(attention_mask, dim=1, keepdim=True)
            mean_embeddings = summed_embeddings / summed_mask
            
            return mean_embeddings.cpu().numpy().flatten()

    def calculate_sentence_transformer_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using Sentence Transformers"""
        if not self.sentence_model:
            return 0.0
        
        if not text1 or not text2:
            return 0.0
        
        try:
            # Check cache first
            cache_key1 = self._get_cache_key(text1, 'sentence_transformer')
            cache_key2 = self._get_cache_key(text2, 'sentence_transformer')
            
            if cache_key1 in self.embedding_cache:
                embedding1 = self.embedding_cache[cache_key1]
            else:
                embedding1 = self.sentence_model.encode(self.preprocess_text(text1))
                self._add_to_cache(cache_key1, embedding1)
            
            if cache_key2 in self.embedding_cache:
                embedding2 = self.embedding_cache[cache_key2]
            else:
                embedding2 = self.sentence_model.encode(self.preprocess_text(text2))
                self._add_to_cache(cache_key2, embedding2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Error in Sentence Transformer similarity calculation: {e}")
            return 0.0

    def calculate_lsa_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using Latent Semantic Analysis (LSA)"""
        if not text1 or not text2:
            return 0.0
        
        try:
            # Preprocess texts
            processed_text1 = self.preprocess_text(text1)
            processed_text2 = self.preprocess_text(text2)
            
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([processed_text1, processed_text2])
            
            # Apply LSA
            if not self.lsa_fitted:
                lsa_matrix = self.lsa.fit_transform(tfidf_matrix)
                self.lsa_fitted = True
            else:
                lsa_matrix = self.lsa.transform(tfidf_matrix)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(lsa_matrix[0:1], lsa_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Error in LSA similarity calculation: {e}")
            return 0.0

    def calculate_combined_similarity(self, text1: str, text2: str, 
                                    weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Calculate combined similarity using multiple methods"""
        if weights is None:
            weights = {
                'tfidf': 0.3,
                'bert': 0.2,
                'sentence_transformer': 0.3,
                'lsa': 0.2
            }
        
        results = {}
        
        # Calculate individual similarities
        if weights.get('tfidf', 0) > 0:
            results['tfidf'] = self.calculate_tfidf_similarity(text1, text2)
        
        if weights.get('bert', 0) > 0:
            results['bert'] = self.calculate_bert_similarity(text1, text2)
        
        if weights.get('sentence_transformer', 0) > 0:
            results['sentence_transformer'] = self.calculate_sentence_transformer_similarity(text1, text2)
        
        if weights.get('lsa', 0) > 0:
            results['lsa'] = self.calculate_lsa_similarity(text1, text2)
        
        # Calculate weighted average
        combined_score = 0.0
        total_weight = 0.0
        
        for method, score in results.items():
            weight = weights.get(method, 0)
            combined_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            combined_score /= total_weight
        
        results['combined'] = combined_score
        
        return results

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using the best available method"""
        # Prefer Sentence Transformer if available, otherwise fall back to BERT, then TF-IDF
        if self.sentence_model:
            return self.calculate_sentence_transformer_similarity(text1, text2)
        elif self.bert_model:
            return self.calculate_bert_similarity(text1, text2)
        else:
            return self.calculate_tfidf_similarity(text1, text2)

    def batch_similarity_calculation(self, texts: List[str], reference_text: str) -> List[float]:
        """Calculate similarity scores for multiple texts against a reference text"""
        similarities = []
        
        for text in texts:
            similarity = self.calculate_semantic_similarity(text, reference_text)
            similarities.append(similarity)
        
        return similarities

    def find_most_similar(self, query_text: str, candidate_texts: List[str], 
                         top_k: int = 5) -> List[Tuple[int, float]]:
        """Find the most similar texts to a query text"""
        similarities = self.batch_similarity_calculation(candidate_texts, query_text)
        
        # Create list of (index, similarity) pairs
        indexed_similarities = [(i, sim) for i, sim in enumerate(similarities)]
        
        # Sort by similarity in descending order
        indexed_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        return indexed_similarities[:top_k]

    def benchmark_methods(self, text1: str, text2: str) -> Dict[str, Dict[str, float]]:
        """Benchmark different similarity methods for performance and accuracy"""
        methods = {
            'tfidf': self.calculate_tfidf_similarity,
            'bert': self.calculate_bert_similarity,
            'sentence_transformer': self.calculate_sentence_transformer_similarity,
            'lsa': self.calculate_lsa_similarity
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            start_time = time.time()
            
            try:
                similarity = method_func(text1, text2)
                execution_time = time.time() - start_time
                
                results[method_name] = {
                    'similarity': similarity,
                    'execution_time': execution_time,
                    'success': True
                }
            except Exception as e:
                execution_time = time.time() - start_time
                results[method_name] = {
                    'similarity': 0.0,
                    'execution_time': execution_time,
                    'success': False,
                    'error': str(e)
                }
        
        return results

    def clear_cache(self):
        """Clear the embedding cache"""
        self.embedding_cache.clear()

    def get_cache_info(self) -> Dict[str, int]:
        """Get information about the cache"""
        return {
            'cache_size': len(self.embedding_cache),
            'max_cache_size': self.max_cache_size
        }

