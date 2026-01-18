"""
Hirify Services Package

Core services for resume parsing and job matching:
- nlp_service: Unified NLP preprocessing
- embedding_engine: Semantic similarity using Sentence Transformers
- semantic_skills: Embedding-based skill extraction and matching
- matching_engine: Resume-job matching
"""

# Document parsing
from .document_validator import DocumentValidator, DocumentValidationError
from .pdf_parser import PDFParser, PDFParsingError
from .docx_parser import DOCXParser, DOCXParsingError
from .document_parser import DocumentParserService, DocumentParsingError

# NLP service
from .nlp_service import NLPService, nlp_service, ProcessedText

# Embedding-based similarity engine
from .embedding_engine import SimilarityEngine, similarity_engine

# Semantic skills extraction
from .semantic_skills import SemanticSkillsExtractor, semantic_skills_extractor

# Matching engine
from .matching_engine import MatchingEngine, matching_engine, MatchResult, MatchScore

# Embedding utilities
from .embedding_utils import embedding_to_bytes, bytes_to_embedding

# NLTK setup
from .nltk_setup import download_nltk_data, check_nltk_data

__all__ = [
    # Document parsing
    "DocumentValidator",
    "DocumentValidationError",
    "PDFParser",
    "PDFParsingError",
    "DOCXParser",
    "DOCXParsingError",
    "DocumentParserService",
    "DocumentParsingError",
    # NLP
    "NLPService",
    "nlp_service",
    "ProcessedText",
    # Similarity
    "SimilarityEngine",
    "similarity_engine",
    # Skills
    "SemanticSkillsExtractor",
    "semantic_skills_extractor",
    # Matching
    "MatchingEngine",
    "matching_engine",
    "MatchResult",
    "MatchScore",
    # Utilities
    "embedding_to_bytes",
    "bytes_to_embedding",
    "download_nltk_data",
    "check_nltk_data",
]
