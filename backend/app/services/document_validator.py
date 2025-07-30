"""
Document validation service for file type and size checking.
"""
import mimetypes
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
# No longer using python-magic to avoid C-binding issues
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class DocumentValidationError(Exception):
    """Custom exception for document validation errors."""
    pass


class DocumentValidator:
    """Service for validating uploaded documents."""
    
    def __init__(self):
        self.allowed_extensions = settings.ALLOWED_FILE_TYPES
        self.max_file_size = settings.MAX_FILE_SIZE
        
        # MIME type mappings
        self.mime_types = {
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'text/plain': 'txt',
        }
        
        # File signatures (magic numbers) for additional validation
        self.file_signatures = {
            'pdf': [b'%PDF'],
            'doc': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],  # OLE compound document
            'docx': [b'PK\x03\x04'],  # ZIP archive (DOCX is a ZIP file)
        }
    
    def validate_file(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Validate a file for type, size, and content.
        
        Args:
            file_path: Path to the uploaded file
            original_filename: Original filename from upload
            
        Returns:
            Dict containing validation results
            
        Raises:
            DocumentValidationError: If validation fails
        """
        try:
            validation_result = {
                'is_valid': True,
                'file_type': None,
                'file_size': 0,
                'mime_type': None,
                'errors': [],
                'warnings': []
            }
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise DocumentValidationError(f"File not found: {file_path}")
            
            # Get file size
            file_size = os.path.getsize(file_path)
            validation_result['file_size'] = file_size
            
            # Validate file size
            if file_size > self.max_file_size:
                validation_result['is_valid'] = False
                validation_result['errors'].append(
                    f"File size ({file_size} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)"
                )
            
            if file_size == 0:
                validation_result['is_valid'] = False
                validation_result['errors'].append("File is empty")
            
            # Validate file extension
            file_extension = Path(original_filename).suffix.lower().lstrip('.')
            if file_extension not in self.allowed_extensions:
                validation_result['is_valid'] = False
                validation_result['errors'].append(
                    f"File extension '{file_extension}' is not allowed. Allowed extensions: {self.allowed_extensions}"
                )
            
            # Detect MIME type
            mime_type = self._detect_mime_type(file_path)
            validation_result['mime_type'] = mime_type
            
            # Validate MIME type
            if mime_type not in self.mime_types:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"MIME type '{mime_type}' is not supported")
            else:
                detected_extension = self.mime_types[mime_type]
                validation_result['file_type'] = detected_extension
                
                # Check if extension matches MIME type
                if file_extension != detected_extension:
                    validation_result['warnings'].append(
                        f"File extension '{file_extension}' doesn't match detected type '{detected_extension}'"
                    )
            
            # Validate file signature
            if validation_result['file_type']:
                if not self._validate_file_signature(file_path, validation_result['file_type']):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append("File signature validation failed - file may be corrupted")
            
            # Additional content validation
            content_validation = self._validate_file_content(file_path, validation_result['file_type'])
            validation_result['errors'].extend(content_validation['errors'])
            validation_result['warnings'].extend(content_validation['warnings'])
            
            if content_validation['errors']:
                validation_result['is_valid'] = False
            
            logger.info(f"File validation completed for {original_filename}: {'PASSED' if validation_result['is_valid'] else 'FAILED'}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating file {original_filename}: {str(e)}")
            raise DocumentValidationError(f"Validation failed: {str(e)}")
    
    def _detect_mime_type(self, file_path: str) -> str:
        """Detect MIME type of a file."""
        # Always use mimetypes for broader compatibility
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    def _validate_file_signature(self, file_path: str, file_type: str) -> bool:
        """Validate file signature (magic numbers)."""
        try:
            if file_type not in self.file_signatures:
                return True  # No signature validation for this type
            
            with open(file_path, 'rb') as f:
                file_header = f.read(512)  # Read first 512 bytes
            
            signatures = self.file_signatures[file_type]
            for signature in signatures:
                if file_header.startswith(signature):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating file signature: {str(e)}")
            return False
    
    def _validate_file_content(self, file_path: str, file_type: str) -> Dict[str, List[str]]:
        """Validate file content based on file type."""
        result = {'errors': [], 'warnings': []}
        
        try:
            if file_type == 'pdf':
                result = self._validate_pdf_content(file_path)
            elif file_type in ['doc', 'docx']:
                result = self._validate_document_content(file_path, file_type)
            
        except Exception as e:
            result['errors'].append(f"Content validation failed: {str(e)}")
        
        return result
    
    def _validate_pdf_content(self, file_path: str) -> Dict[str, List[str]]:
        """Validate PDF content."""
        result = {'errors': [], 'warnings': []}
        
        try:
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    result['errors'].append("PDF file contains no pages")
                    return result
                
                # Check if PDF has extractable text
                total_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        total_text += text
                
                if not total_text.strip():
                    result['warnings'].append("PDF appears to contain no extractable text (might be image-based)")
                elif len(total_text.strip()) < 50:
                    result['warnings'].append("PDF contains very little text content")
                
        except Exception as e:
            result['errors'].append(f"PDF validation failed: {str(e)}")
        
        return result
    
    def _validate_document_content(self, file_path: str, file_type: str) -> Dict[str, List[str]]:
        """Validate DOC/DOCX content."""
        result = {'errors': [], 'warnings': []}
        
        try:
            if file_type == 'docx':
                from docx import Document
                
                doc = Document(file_path)
                
                # Check if document has content
                total_text = ""
                for paragraph in doc.paragraphs:
                    total_text += paragraph.text
                
                if not total_text.strip():
                    result['warnings'].append("Document appears to contain no text content")
                elif len(total_text.strip()) < 50:
                    result['warnings'].append("Document contains very little text content")
                    
            elif file_type == 'doc':
                # For .doc files, we'll use a different approach
                # This is a basic check - more sophisticated validation could be added
                result['warnings'].append("DOC file format validation is limited")
                
        except Exception as e:
            result['errors'].append(f"Document validation failed: {str(e)}")
        
        return result
    
    def is_valid_file_type(self, filename: str) -> bool:
        """Quick check if file type is allowed."""
        extension = Path(filename).suffix.lower().lstrip('.')
        return extension in self.allowed_extensions
    
    def get_file_type_from_extension(self, filename: str) -> Optional[str]:
        """Get file type from filename extension."""
        extension = Path(filename).suffix.lower().lstrip('.')
        return extension if extension in self.allowed_extensions else None
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent security issues."""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]
        
        return name + ext
