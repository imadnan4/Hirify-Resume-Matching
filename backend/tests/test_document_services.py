"""
Basic test to verify document parsing services can be imported and initialized.
"""
import pytest
from unittest.mock import patch, MagicMock


def test_import_document_services():
    """Test that all document parsing services can be imported."""
    from app.services import (
        DocumentValidator,
        DocumentValidationError,
        PDFParser,
        PDFParsingError,
        DOCXParser,
        DOCXParsingError,
        DocumentParserService,
        DocumentParsingError
    )
    
    # Test that classes can be instantiated
    validator = DocumentValidator()
    pdf_parser = PDFParser()
    docx_parser = DOCXParser()
    parser_service = DocumentParserService()
    
    assert validator is not None
    assert pdf_parser is not None
    assert docx_parser is not None
    assert parser_service is not None
    
    # Test that exception classes exist
    assert issubclass(DocumentValidationError, Exception)
    assert issubclass(PDFParsingError, Exception)
    assert issubclass(DOCXParsingError, Exception)
    assert issubclass(DocumentParsingError, Exception)


def test_document_validator_basic():
    """Test basic DocumentValidator functionality."""
    from app.services import DocumentValidator
    
    validator = DocumentValidator()
    
    # Test file type validation
    assert validator.is_valid_file_type('test.pdf') is True
    assert validator.is_valid_file_type('test.docx') is True
    assert validator.is_valid_file_type('test.txt') is False
    
    # Test filename sanitization
    sanitized = validator.sanitize_filename('test<file>.pdf')
    assert '<' not in sanitized
    assert '>' not in sanitized


def test_pdf_parser_basic():
    """Test basic PDFParser functionality."""
    from app.services import PDFParser
    
    parser = PDFParser()
    
    assert parser.supported_formats == ['.pdf']


def test_docx_parser_basic():
    """Test basic DOCXParser functionality."""
    from app.services import DOCXParser
    
    parser = DOCXParser()
    
    assert parser.supported_formats == ['.docx', '.doc']


def test_document_parser_service_basic():
    """Test basic DocumentParserService functionality."""
    from app.services import DocumentParserService
    
    service = DocumentParserService()
    
    # Test supported file types
    supported_types = service.get_supported_file_types()
    assert 'pdf' in supported_types
    assert 'docx' in supported_types
    
    # Test file type checking
    assert service.is_file_supported('test.pdf') is True
    assert service.is_file_supported('test.txt') is False
