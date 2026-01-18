"""
Consolidated NLP Service for Hirify
Combines text preprocessing, tokenization, and entity extraction into a single service.
"""
import re
import string
import unicodedata
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import logging

# Initialize NLTK
from app.core.nltk_init import init_nltk
init_nltk()

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer

logger = logging.getLogger(__name__)

# Try to load spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None


@dataclass
class ProcessedText:
    """Container for processed text data"""
    raw_text: str
    cleaned_text: str
    tokens: List[str]
    sentences: List[str]
    entities: List[Dict[str, Any]]
    keywords: List[str]
    statistics: Dict[str, Any]


class NLPService:
    """
    Unified NLP service for all text processing needs.
    Handles preprocessing, tokenization, entity extraction, and keyword extraction.
    """
    
    _instance = None
    _nlp_model = None
    _nlp_loading = False
    _nlp_failed = False
    
    def __new__(cls):
        """Singleton pattern to avoid loading models multiple times"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # NLTK components
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        # Custom stop words for resumes/job descriptions
        self.resume_stop_words = {
            'experience', 'work', 'working', 'worked', 'year', 'years',
            'company', 'position', 'role', 'team', 'responsible', 'responsibilities',
            'etc', 'also', 'including', 'well', 'various', 'using', 'used'
        }
        self.stop_words.update(self.resume_stop_words)
        
        logger.info("NLP Service initialized")
    
    def _load_spacy_model(self):
        """Lazy load spaCy model"""
        if NLPService._nlp_model is not None or NLPService._nlp_loading or NLPService._nlp_failed:
            return
        
        if not SPACY_AVAILABLE:
            NLPService._nlp_failed = True
            return
        
        NLPService._nlp_loading = True
        try:
            NLPService._nlp_model = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            NLPService._nlp_model = None
            NLPService._nlp_failed = True
            logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        finally:
            NLPService._nlp_loading = False
    
    @property
    def nlp(self):
        """Get spaCy model, loading if necessary"""
        self._load_spacy_model()
        return NLPService._nlp_model
    
    # ==================== TEXT CLEANING ====================
    
    def clean_text(self, text: str, aggressive: bool = False) -> str:
        """
        Clean and normalize text for processing.
        
        Args:
            text: Raw text to clean
            aggressive: If True, removes more characters (for embedding)
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', ' ', text)
        
        # Remove phone numbers
        text = re.sub(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', ' ', text)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        
        if aggressive:
            # Remove all non-alphanumeric characters
            text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        else:
            # Keep basic punctuation
            text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def normalize_text(self, text: str) -> str:
        """Light normalization preserving more structure"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[\.]{2,}', '.', text)
        text = re.sub(r'[\,]{2,}', ',', text)
        
        return text.strip()
    
    # ==================== TOKENIZATION ====================
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if not text:
            return []
        return sent_tokenize(text)
    
    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if not text:
            return []
        return word_tokenize(text)
    
    def get_tokens(self, text: str, 
                   remove_stopwords: bool = True,
                   lemmatize: bool = True,
                   min_length: int = 2) -> List[str]:
        """
        Get processed tokens from text.
        
        Args:
            text: Text to tokenize
            remove_stopwords: Remove common stop words
            lemmatize: Apply lemmatization
            min_length: Minimum token length
            
        Returns:
            List of processed tokens
        """
        if not text:
            return []
        
        # Clean and tokenize
        cleaned = self.clean_text(text)
        tokens = self.tokenize_words(cleaned)
        
        # Filter and process
        processed = []
        for token in tokens:
            # Skip short tokens
            if len(token) < min_length:
                continue
            
            # Skip stopwords
            if remove_stopwords and token.lower() in self.stop_words:
                continue
            
            # Lemmatize
            if lemmatize:
                token = self.lemmatizer.lemmatize(token.lower())
            else:
                token = token.lower()
            
            processed.append(token)
        
        return processed
    
    # ==================== ENTITY EXTRACTION ====================
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text using spaCy.
        
        Returns list of dicts with: text, label, start, end
        """
        if not self.nlp or not text:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
            
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """
        Extract important keywords from text.
        Uses noun phrases and important POS tags.
        """
        if not text:
            return []
        
        keywords = set()
        
        # Method 1: Use spaCy if available
        if self.nlp:
            try:
                doc = self.nlp(text)
                
                # Extract noun chunks
                for chunk in doc.noun_chunks:
                    keyword = chunk.text.lower().strip()
                    if len(keyword) > 2 and keyword not in self.stop_words:
                        keywords.add(keyword)
                
                # Extract important individual tokens
                for token in doc:
                    if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                        not token.is_stop and 
                        not token.is_punct and 
                        len(token.text) > 2):
                        keywords.add(token.text.lower())
                        
            except Exception as e:
                logger.error(f"Error in spaCy keyword extraction: {e}")
        
        # Method 2: Fallback to simple extraction
        if not keywords:
            tokens = self.get_tokens(text, remove_stopwords=True, lemmatize=True)
            keywords = set(tokens)
        
        # Sort by length (prefer compound terms) and limit
        sorted_keywords = sorted(keywords, key=lambda x: (-len(x.split()), x))
        return sorted_keywords[:top_n]
    
    # ==================== MAIN PROCESSING ====================
    
    def process(self, text: str) -> ProcessedText:
        """
        Full text processing pipeline.
        
        Args:
            text: Raw text to process
            
        Returns:
            ProcessedText with all extracted information
        """
        if not text:
            return ProcessedText(
                raw_text="",
                cleaned_text="",
                tokens=[],
                sentences=[],
                entities=[],
                keywords=[],
                statistics={}
            )
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Tokenize
        tokens = self.get_tokens(text)
        sentences = self.tokenize_sentences(text)
        
        # Extract entities and keywords
        entities = self.extract_entities(text)
        keywords = self.extract_keywords(text)
        
        # Generate statistics
        statistics = {
            'raw_char_count': len(text),
            'clean_char_count': len(cleaned_text),
            'word_count': len(text.split()),
            'token_count': len(tokens),
            'sentence_count': len(sentences),
            'entity_count': len(entities),
            'keyword_count': len(keywords),
            'unique_tokens': len(set(tokens)),
            'avg_words_per_sentence': len(tokens) / len(sentences) if sentences else 0
        }
        
        return ProcessedText(
            raw_text=text,
            cleaned_text=cleaned_text,
            tokens=tokens,
            sentences=sentences,
            entities=entities,
            keywords=keywords,
            statistics=statistics
        )
    
    # ==================== UTILITY METHODS ====================
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Apply stemming to tokens"""
        return [self.stemmer.stem(token) for token in tokens]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """Apply lemmatization to tokens"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def get_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Extract n-grams from text"""
        tokens = self.get_tokens(text, remove_stopwords=False, lemmatize=False)
        if len(tokens) < n:
            return []
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    def calculate_text_similarity_simple(self, text1: str, text2: str) -> float:
        """
        Simple Jaccard similarity between two texts.
        For semantic similarity, use SimilarityEngine instead.
        """
        if not text1 or not text2:
            return 0.0
        
        tokens1 = set(self.get_tokens(text1))
        tokens2 = set(self.get_tokens(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0


# Create singleton instance for easy import
nlp_service = NLPService()
