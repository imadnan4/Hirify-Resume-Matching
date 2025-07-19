"""
Mock Text Preprocessing Service for Resume Parser
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TextPreprocessingResult:
    """Result from text preprocessing"""
    success: bool
    original_text: str
    cleaned_text: str
    tokens: List[str]
    sentences: List[str]
    statistics: Dict[str, Any]
    processing_time: float

class TextPreprocessingService:
    """Mock text preprocessing service"""
    
    def __init__(self):
        self.name = "Mock Text Preprocessing Service"
    
    def preprocess_text(self, text: str) -> TextPreprocessingResult:
        """
        Preprocess text for analysis
        
        Args:
            text: Text to preprocess
            
        Returns:
            TextPreprocessingResult with mock data
        """
        start_time = datetime.now()
        
        if not text:
            return TextPreprocessingResult(
                success=False,
                original_text="",
                cleaned_text="",
                tokens=[],
                sentences=[],
                statistics={},
                processing_time=0.0
            )
        
        # Mock preprocessing
        cleaned_text = text.lower().strip()
        tokens = cleaned_text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Mock statistics
        statistics = {
            "word_count": len(tokens),
            "sentence_count": len(sentences),
            "character_count": len(text),
            "avg_words_per_sentence": len(tokens) / len(sentences) if sentences else 0
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return TextPreprocessingResult(
            success=True,
            original_text=text,
            cleaned_text=cleaned_text,
            tokens=tokens,
            sentences=sentences,
            statistics=statistics,
            processing_time=processing_time
        )
