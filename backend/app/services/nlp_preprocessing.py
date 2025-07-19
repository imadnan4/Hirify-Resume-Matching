"""
NLP Preprocessing Pipeline for Resume Parser
"""
import re
import string
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ProcessedText:
    """Container for processed text data"""
    raw_text: str
    cleaned_text: str
    tokens: List[str]
    sentences: List[str]
    statistics: Dict[str, Any]

class NLPPreprocessingPipeline:
    """Basic NLP preprocessing pipeline"""
    
    def __init__(self):
        self.name = "NLP Preprocessing Pipeline"
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how',
            'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then',
            'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into',
            'him', 'time', 'has', 'two', 'more', 'very', 'after', 'words', 'long',
            'than', 'first', 'been', 'call', 'who', 'oil', 'its', 'now', 'find',
            'could', 'made', 'may', 'part'
        }
    
    def preprocess_text(self, text: str) -> ProcessedText:
        """
        Preprocess text for NLP analysis
        
        Args:
            text: Raw text to process
            
        Returns:
            ProcessedText object with cleaned text and tokens
        """
        if not text:
            return ProcessedText(
                raw_text="",
                cleaned_text="",
                tokens=[],
                sentences=[],
                statistics={}
            )
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Tokenize
        tokens = self.tokenize(cleaned_text)
        
        # Extract sentences
        sentences = self.extract_sentences(cleaned_text)
        
        # Generate statistics
        statistics = self.generate_statistics(text, cleaned_text, tokens, sentences)
        
        return ProcessedText(
            raw_text=text,
            cleaned_text=cleaned_text,
            tokens=tokens,
            sentences=sentences,
            statistics=statistics
        )
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep letters, numbers, and basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove excessive punctuation
        text = re.sub(r'[\.]{2,}', '.', text)
        text = re.sub(r'[\,]{2,}', ',', text)
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """Basic tokenization"""
        if not text:
            return []
        
        # Split into words
        words = re.findall(r'\b\w+\b', text)
        
        # Remove stop words and short words
        tokens = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        return tokens
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        if not text:
            return []
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def generate_statistics(self, raw_text: str, cleaned_text: str, 
                          tokens: List[str], sentences: List[str]) -> Dict[str, Any]:
        """Generate text statistics"""
        return {
            'raw_char_count': len(raw_text),
            'clean_char_count': len(cleaned_text),
            'word_count': len(raw_text.split()),
            'token_count': len(tokens),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': len(tokens) / len(sentences) if sentences else 0,
            'unique_tokens': len(set(tokens)),
            'vocab_richness': len(set(tokens)) / len(tokens) if tokens else 0
        }
