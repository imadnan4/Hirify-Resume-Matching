"""
Main document parsing service that coordinates all parsers.
"""
import os
import uuid
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from datetime import datetime

from .document_validator import DocumentValidator, DocumentValidationError
from .pdf_parser import PDFParser, PDFParsingError
from .docx_parser import DOCXParser, DOCXParsingError
from ..core.config import settings

logger = logging.getLogger(__name__)


class DocumentParsingError(Exception):
    """Main exception for document parsing errors."""
    pass


class DocumentParserService:
    """
    Main service for parsing documents.
    Coordinates validation and different parsing strategies.
    """
    
    def __init__(self):
        self.validator = DocumentValidator()
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        
        # Ensure upload directory exists
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Temporary directory for processing
        self.temp_dir = Path(tempfile.gettempdir()) / "hirify"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def parse_document(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Parse a document and extract all relevant information.
        
        Args:
            file_path: Path to the uploaded file
            original_filename: Original filename from upload
            
        Returns:
            Dict containing all extracted information
            
        Raises:
            DocumentParsingError: If parsing fails
        """
        try:
            start_time = datetime.now()
            
            result = {
                'file_info': {
                    'original_filename': original_filename,
                    'file_path': file_path,
                    'processing_started': start_time.isoformat()
                },
                'validation': {},
                'extraction': {},
                'processing_time': 0.0,
                'status': 'processing',
                'errors': [],
                'warnings': []
            }
            
            # Step 1: Validate the document
            logger.info(f"Starting document validation for {original_filename}")
            try:
                validation_result = self.validator.validate_file(file_path, original_filename)
                result['validation'] = validation_result
                
                if not validation_result['is_valid']:
                    result['status'] = 'failed'
                    result['errors'].extend(validation_result['errors'])
                    result['warnings'].extend(validation_result['warnings'])
                    raise DocumentParsingError(f"Document validation failed: {validation_result['errors']}")
                
                # Add any validation warnings
                result['warnings'].extend(validation_result['warnings'])
                
            except DocumentValidationError as e:
                result['status'] = 'failed'
                result['errors'].append(f"Validation error: {str(e)}")
                raise DocumentParsingError(f"Document validation failed: {str(e)}")
            
            # Step 2: Extract text based on file type
            logger.info(f"Starting text extraction for {original_filename}")
            file_type = result['validation']['file_type']
            
            try:
                if file_type == 'pdf':
                    extraction_result = self.pdf_parser.extract_text(file_path)
                elif file_type in ['doc', 'docx']:
                    extraction_result = self.docx_parser.extract_text(file_path)
                else:
                    raise DocumentParsingError(f"Unsupported file type: {file_type}")
                
                result['extraction'] = extraction_result
                
                # Add extraction warnings and errors
                result['warnings'].extend(extraction_result.get('warnings', []))
                result['errors'].extend(extraction_result.get('errors', []))
                
            except (PDFParsingError, DOCXParsingError) as e:
                result['status'] = 'failed'
                result['errors'].append(f"Extraction error: {str(e)}")
                raise DocumentParsingError(f"Text extraction failed: {str(e)}")
            
            # Step 3: Post-process and validate extraction quality
            logger.info(f"Post-processing extracted content for {original_filename}")
            result = self._post_process_extraction(result)
            
            # Step 4: Generate summary
            result['summary'] = self._generate_extraction_summary(result)
            
            # Calculate processing time
            end_time = datetime.now()
            result['processing_time'] = (end_time - start_time).total_seconds()
            result['file_info']['processing_completed'] = end_time.isoformat()
            
            # Determine final status
            if result['errors']:
                result['status'] = 'completed_with_errors'
            else:
                result['status'] = 'completed'
            
            logger.info(f"Document parsing completed for {original_filename} in {result['processing_time']:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing document {original_filename}: {str(e)}")
            result['status'] = 'failed'
            result['errors'].append(f"Parsing error: {str(e)}")
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # Return partial results even on failure
            return result
    
    def _post_process_extraction(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process extraction results to improve quality."""
        try:
            extraction = result.get('extraction', {})
            
            if not extraction.get('text'):
                result['warnings'].append("No text was extracted from the document")
                return result
            
            # Clean and normalize text
            text = extraction['text']
            
            # Basic text cleaning
            text = self._clean_text(text)
            
            # Update the cleaned text
            extraction['text'] = text
            
            # Generate text statistics
            extraction['text_statistics'] = self._generate_text_statistics(text)
            
            # Analyze content quality
            quality_analysis = self._analyze_content_quality(text)
            extraction['quality_analysis'] = quality_analysis
            
            # Add quality warnings
            if quality_analysis['warnings']:
                result['warnings'].extend(quality_analysis['warnings'])
            
        except Exception as e:
            logger.error(f"Error in post-processing: {str(e)}")
            result['errors'].append(f"Post-processing error: {str(e)}")
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return text
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Replace multiple newlines with double newline
        
        # Remove common artifacts
        text = text.replace('\u200b', '')  # Remove zero-width space
        text = text.replace('\ufeff', '')  # Remove BOM
        
        # Normalize unicode characters
        text = text.replace(''', "'")  # Replace smart quotes
        text = text.replace(''', "'")
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        text = text.replace('—', '--')  # Replace em dash
        text = text.replace('–', '-')   # Replace en dash
        text = text.replace('…', '...')  # Replace ellipsis
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _generate_text_statistics(self, text: str) -> Dict[str, Any]:
        """Generate statistics about the extracted text."""
        if not text:
            return {
                'character_count': 0,
                'word_count': 0,
                'line_count': 0,
                'paragraph_count': 0,
                'sentence_count': 0,
                'average_word_length': 0.0,
                'average_sentence_length': 0.0
            }
        
        import re
        
        # Basic counts
        char_count = len(text)
        words = text.split()
        word_count = len(words)
        lines = text.split('\n')
        line_count = len(lines)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Sentence count (simple approach)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Average calculations
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            'character_count': char_count,
            'word_count': word_count,
            'line_count': line_count,
            'paragraph_count': paragraph_count,
            'sentence_count': sentence_count,
            'average_word_length': round(avg_word_length, 2),
            'average_sentence_length': round(avg_sentence_length, 2)
        }
    
    def _analyze_content_quality(self, text: str) -> Dict[str, Any]:
        """Analyze the quality of extracted content."""
        analysis = {
            'quality_score': 0.0,
            'warnings': [],
            'indicators': {
                'has_contact_info': False,
                'has_professional_content': False,
                'has_structured_sections': False,
                'text_coherence': 'unknown'
            }
        }
        
        if not text:
            analysis['warnings'].append("No text content to analyze")
            return analysis
        
        import re
        
        # Check for contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
        
        if re.search(email_pattern, text) or re.search(phone_pattern, text):
            analysis['indicators']['has_contact_info'] = True
        
        # Check for professional content
        professional_keywords = [
            'experience', 'skills', 'education', 'work', 'employment',
            'project', 'achievement', 'certification', 'degree', 'university'
        ]
        
        professional_matches = sum(1 for keyword in professional_keywords if keyword.lower() in text.lower())
        if professional_matches >= 3:
            analysis['indicators']['has_professional_content'] = True
        
        # Check for structured sections
        section_patterns = [
            r'(?i)^(experience|education|skills|summary|objective)',
            r'(?i)(work\s+history|employment|career)',
            r'(?i)(technical\s+skills|competencies)',
            r'(?i)(certifications|achievements|projects)'
        ]
        
        section_matches = sum(1 for pattern in section_patterns if re.search(pattern, text))
        if section_matches >= 2:
            analysis['indicators']['has_structured_sections'] = True
        
        # Simple text coherence check
        words = text.split()
        if len(words) > 0:
            alpha_ratio = sum(1 for word in words if word.isalpha()) / len(words)
            if alpha_ratio > 0.8:
                analysis['indicators']['text_coherence'] = 'good'
            elif alpha_ratio > 0.6:
                analysis['indicators']['text_coherence'] = 'fair'
            else:
                analysis['indicators']['text_coherence'] = 'poor'
                analysis['warnings'].append("Text appears to have low coherence - may contain extraction artifacts")
        
        # Calculate quality score
        quality_score = 0.0
        if analysis['indicators']['has_contact_info']:
            quality_score += 25
        if analysis['indicators']['has_professional_content']:
            quality_score += 35
        if analysis['indicators']['has_structured_sections']:
            quality_score += 25
        if analysis['indicators']['text_coherence'] == 'good':
            quality_score += 15
        elif analysis['indicators']['text_coherence'] == 'fair':
            quality_score += 10
        
        analysis['quality_score'] = quality_score
        
        # Add warnings based on quality
        if quality_score < 30:
            analysis['warnings'].append("Low quality extraction detected - document may not be a standard resume")
        elif quality_score < 50:
            analysis['warnings'].append("Medium quality extraction - some information may be missing")
        
        return analysis
    
    def _generate_extraction_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the extraction process."""
        summary = {
            'success': result['status'] in ['completed', 'completed_with_errors'],
            'file_type': result.get('validation', {}).get('file_type', 'unknown'),
            'extraction_method': result.get('extraction', {}).get('extraction_method', 'unknown'),
            'text_extracted': bool(result.get('extraction', {}).get('text')),
            'quality_score': result.get('extraction', {}).get('quality_analysis', {}).get('quality_score', 0.0),
            'warnings_count': len(result.get('warnings', [])),
            'errors_count': len(result.get('errors', [])),
            'processing_time': result.get('processing_time', 0.0)
        }
        
        # Add text statistics if available
        text_stats = result.get('extraction', {}).get('text_statistics', {})
        if text_stats:
            summary['word_count'] = text_stats.get('word_count', 0)
            summary['character_count'] = text_stats.get('character_count', 0)
        
        return summary
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> str:
        """
        Save uploaded file to disk and return the file path.
        
        Args:
            file_content: Binary content of the uploaded file
            original_filename: Original filename from upload
            
        Returns:
            Path to the saved file
        """
        try:
            # Generate unique filename
            file_extension = Path(original_filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save to upload directory
            file_path = self.upload_dir / unique_filename
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Saved uploaded file: {original_filename} -> {file_path}")
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving uploaded file {original_filename}: {str(e)}")
            raise DocumentParsingError(f"Failed to save uploaded file: {str(e)}")
    
    def cleanup_temp_files(self, file_path: str) -> None:
        """Clean up temporary files."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary file {file_path}: {str(e)}")
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file types."""
        return self.validator.allowed_extensions
    
    def is_file_supported(self, filename: str) -> bool:
        """Check if file type is supported."""
        return self.validator.is_valid_file_type(filename)
