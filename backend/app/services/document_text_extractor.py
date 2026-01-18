"""
Unified document text extractor for various file formats.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .pdf_parser import PDFParser, PDFParsingError
from .docx_parser import DOCXParser, DOCXParsingError

logger = logging.getLogger(__name__)


class DocumentTextExtractor:
    """Service for extracting text from various document formats."""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        
        # Supported formats mapping
        self.format_handlers = {
            '.pdf': self._extract_from_pdf,
            '.docx': self._extract_from_docx,
            '.doc': self._extract_from_doc
        }
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dict containing extracted text and metadata
            
        Raises:
            ValueError: If file format is not supported
            Exception: If text extraction fails
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file extension
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension not in self.format_handlers:
                raise ValueError(
                    f"Unsupported file format: {file_extension}. "
                    f"Supported formats: {list(self.format_handlers.keys())}"
                )
            
            # Extract text using appropriate handler
            handler = self.format_handlers[file_extension]
            result = handler(file_path)
            
            # Add common metadata
            result['file_info'] = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_extension': file_extension,
                'file_size': os.path.getsize(file_path)
            }
            
            logger.info(f"Successfully extracted text from {file_path} using {result.get('extraction_method', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF file."""
        try:
            return self.pdf_parser.extract_text(file_path)
        except PDFParsingError as e:
            logger.error(f"PDF parsing failed for {file_path}: {str(e)}")
            raise
    
    def _extract_from_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract text from DOCX file."""
        try:
            return self.docx_parser.extract_text(file_path)
        except DOCXParsingError as e:
            logger.error(f"DOCX parsing failed for {file_path}: {str(e)}")
            raise
    
    def _extract_from_doc(self, file_path: str) -> Dict[str, Any]:
        """Extract text from DOC file (legacy format)."""
        try:
            # DOC files are handled by the DOCX parser with limitations
            result = self.docx_parser.extract_text(file_path)
            result['warnings'].append("DOC format has limited extraction capabilities compared to DOCX")
            return result
        except DOCXParsingError as e:
            logger.error(f"DOC parsing failed for {file_path}: {str(e)}")
            raise
    
    def get_text_only(self, file_path: str) -> str:
        """
        Extract only the text content from a document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text as string
        """
        try:
            result = self.extract_text(file_path)
            return result.get('text', '')
        except Exception as e:
            logger.warning(f"Failed to extract text from {file_path}: {str(e)}")
            return ''
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.format_handlers
    
    def get_supported_formats(self) -> list:
        """Get list of supported file formats."""
        return list(self.format_handlers.keys())
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a document file for text extraction.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dict with validation results
        """
        validation_result = {
            'is_valid': False,
            'file_exists': False,
            'is_supported_format': False,
            'can_extract_text': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                validation_result['errors'].append("File does not exist")
                return validation_result
            
            validation_result['file_exists'] = True
            
            # Check if format is supported
            if not self.is_supported_format(file_path):
                file_extension = Path(file_path).suffix.lower()
                validation_result['errors'].append(
                    f"Unsupported file format: {file_extension}"
                )
                return validation_result
            
            validation_result['is_supported_format'] = True
            
            # Try to extract a small sample to verify file integrity
            try:
                result = self.extract_text(file_path)
                if result.get('text'):
                    validation_result['can_extract_text'] = True
                    validation_result['is_valid'] = True
                else:
                    validation_result['warnings'].append("No text could be extracted from the file")
                
                # Add any extraction warnings
                if result.get('warnings'):
                    validation_result['warnings'].extend(result['warnings'])
                
                # Add any extraction errors
                if result.get('errors'):
                    validation_result['errors'].extend(result['errors'])
                    
            except Exception as e:
                validation_result['errors'].append(f"Text extraction failed: {str(e)}")
            
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
        
        return validation_result
