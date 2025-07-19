import re
import string
import unicodedata
import os
from typing import List, Optional

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
import spacy

class TextPreprocessor:
    """Comprehensive text preprocessing service for NLP tasks"""

    def __init__(self):
        self._setup_nltk_data()
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
            print("Warning: spaCy model 'en_core_web_sm' not found. Some features may be limited.")

    def _setup_nltk_data(self):
        """Setup NLTK data path and download if needed"""
        # Set NLTK data path from environment variable
        nltk_data_path = os.environ.get('NLTK_DATA', '/opt/venv/nltk_data')
        if nltk_data_path not in nltk.data.path:
            nltk.data.path.insert(0, nltk_data_path)
        
        # Try to find required data, download only if not found
        required_data = [
            ('tokenizers/punkt', 'punkt'),
            ('corpora/stopwords', 'stopwords'),
            ('corpora/wordnet', 'wordnet')
        ]
        
        for data_path, download_name in required_data:
            try:
                nltk.data.find(data_path)
            except LookupError:
                print(f"NLTK data {download_name} not found, attempting download...")
                try:
                    nltk.download(download_name, download_dir=nltk_data_path)
                except Exception as e:
                    print(f"Warning: Could not download NLTK data {download_name}: {e}")

    def clean_text(self, text: str) -> str:
        """Clean and normalize text for processing"""
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
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove Unicode characters
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences"""
        if not text:
            return []
        return sent_tokenize(text)

    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if not text:
            return []
        return word_tokenize(text)

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list"""
        return [token for token in tokens if token.lower() not in self.stop_words]

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Apply stemming to tokens"""
        return [self.stemmer.stem(token) for token in tokens]

    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """Apply lemmatization to tokens"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def remove_short_tokens(self, tokens: List[str], min_length: int = 2) -> List[str]:
        """Remove tokens shorter than minimum length"""
        return [token for token in tokens if len(token) >= min_length]

    def extract_entities_spacy(self, text: str) -> List[dict]:
        """Extract named entities using spaCy"""
        if not self.nlp or not text:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities

    def preprocess_text(self, text: str, 
                      remove_stopwords: bool = True,
                      apply_stemming: bool = False,
                      apply_lemmatization: bool = True,
                      min_token_length: int = 2) -> List[str]:
        """Complete text preprocessing pipeline"""
        
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Tokenize into words
        tokens = self.tokenize_words(cleaned_text)
        
        # Remove short tokens
        tokens = self.remove_short_tokens(tokens, min_token_length)
        
        # Remove stopwords
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Apply stemming or lemmatization
        if apply_stemming:
            tokens = self.stem_tokens(tokens)
        elif apply_lemmatization:
            tokens = self.lemmatize_tokens(tokens)
        
        return tokens

    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text using spaCy"""
        if not self.nlp or not text:
            return []
        
        doc = self.nlp(text)
        phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:  # Multi-word phrases
                phrases.append(chunk.text.lower())
        
        # Remove duplicates and return top phrases
        unique_phrases = list(set(phrases))
        return unique_phrases[:max_phrases]

    def get_text_statistics(self, text: str) -> dict:
        """Get basic text statistics"""
        if not text:
            return {
                'character_count': 0,
                'word_count': 0,
                'sentence_count': 0,
                'avg_word_length': 0,
                'avg_sentence_length': 0
            }
        
        sentences = self.tokenize_sentences(text)
        words = self.tokenize_words(text)
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }

