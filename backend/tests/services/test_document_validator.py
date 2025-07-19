"""
Unit tests for document validation service.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.services.document_validator import DocumentValidator, DocumentValidationError


class TestDocumentValidator:
    """Test cases for DocumentValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DocumentValidator()
    
    def test_init(self):
        """Test DocumentValidator initialization."""
        assert self.validator.allowed_extensions == ['pdf', 'doc', 'docx']
        assert self.validator.max_file_size == 10 * 1024 * 1024  # 10MB
        assert 'application/pdf' in self.validator.mime_types
        assert 'pdf' in self.validator.file_signatures
    
    def test_is_valid_file_type_valid(self):
        """Test is_valid_file_type with valid extensions."""
        assert self.validator.is_valid_file_type('resume.pdf') is True
        assert self.validator.is_valid_file_type('document.docx') is True
        assert self.validator.is_valid_file_type('file.doc') is True
        assert self.validator.is_valid_file_type('TEST.PDF') is True  # Case insensitive
    
    def test_is_valid_file_type_invalid(self):
        """Test is_valid_file_type with invalid extensions."""
        assert self.validator.is_valid_file_type('image.jpg') is False
        assert self.validator.is_valid_file_type('text.txt') is False
        assert self.validator.is_valid_file_type('archive.zip') is False
        assert self.validator.is_valid_file_type('noextension') is False
    
    def test_get_file_type_from_extension(self):
        """Test get_file_type_from_extension method."""
        assert self.validator.get_file_type_from_extension('resume.pdf') == 'pdf'
        assert self.validator.get_file_type_from_extension('document.docx') == 'docx'
        assert self.validator.get_file_type_from_extension('file.doc') == 'doc'
        assert self.validator.get_file_type_from_extension('invalid.txt') is None
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test dangerous characters removal
        assert self.validator.sanitize_filename('file<>name.pdf') == 'file__name.pdf'
        assert self.validator.sanitize_filename('file:name.pdf') == 'file_name.pdf'
        assert self.validator.sanitize_filename('file|name.pdf') == 'file_name.pdf'
        
        # Test path component removal
        assert self.validator.sanitize_filename('/path/to/file.pdf') == 'file.pdf'
        assert self.validator.sanitize_filename('..\\..\\file.pdf') == 'file.pdf'
        
        # Test length limitation
        long_name = 'a' * 250 + '.pdf'
        sanitized = self.validator.sanitize_filename(long_name)
        assert len(sanitized) <= 204  # 200 chars + .pdf
    
    def test_validate_file_not_found(self):
        """Test validation when file doesn't exist."""
        with pytest.raises(DocumentValidationError, match="File not found"):
            self.validator.validate_file('/nonexistent/file.pdf', 'test.pdf')
    
    def test_validate_file_empty_file(self):
        """Test validation with empty file."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result = self.validator.validate_file(tmp_path, 'test.pdf')
            assert result['is_valid'] is False
            assert any('empty' in error.lower() for error in result['errors'])
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_too_large(self):
        """Test validation with file too large."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Write content larger than max size
            large_content = b'x' * (self.validator.max_file_size + 1)
            tmp.write(large_content)
            tmp_path = tmp.name
        
        try:
            result = self.validator.validate_file(tmp_path, 'test.pdf')
            assert result['is_valid'] is False
            assert any('exceeds maximum' in error for error in result['errors'])
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_invalid_extension(self):
        """Test validation with invalid file extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            result = self.validator.validate_file(tmp_path, 'test.txt')
            assert result['is_valid'] is False
            assert any('not allowed' in error for error in result['errors'])
        finally:
            os.unlink(tmp_path)
    
    @patch('app.services.document_validator.magic.from_file')
    def test_detect_mime_type_with_magic(self, mock_magic):
        """Test MIME type detection using python-magic."""
        mock_magic.return_value = 'application/pdf'
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            mime_type = self.validator._detect_mime_type(tmp_path)
            assert mime_type == 'application/pdf'
            mock_magic.assert_called_once_with(tmp_path, mime=True)
        finally:
            os.unlink(tmp_path)
    
    @patch('app.services.document_validator.magic.from_file')
    @patch('app.services.document_validator.mimetypes.guess_type')
    def test_detect_mime_type_fallback(self, mock_mimetypes, mock_magic):
        """Test MIME type detection fallback to mimetypes."""
        mock_magic.side_effect = Exception("Magic failed")
        mock_mimetypes.return_value = ('application/pdf', None)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            mime_type = self.validator._detect_mime_type(tmp_path)
            assert mime_type == 'application/pdf'
            mock_mimetypes.assert_called_once_with(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_signature_pdf(self):
        """Test file signature validation for PDF."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4\n%test content')
            tmp_path = tmp.name
        
        try:
            result = self.validator._validate_file_signature(tmp_path, 'pdf')
            assert result is True
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_signature_invalid(self):
        """Test file signature validation with invalid signature."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'invalid content')
            tmp_path = tmp.name
        
        try:
            result = self.validator._validate_file_signature(tmp_path, 'pdf')
            assert result is False
        finally:
            os.unlink(tmp_path)
    
    @patch('app.services.document_validator.pdfplumber.open')
    def test_validate_pdf_content_valid(self, mock_pdfplumber):
        """Test PDF content validation with valid content."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a test resume with sufficient content"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4\n%test')
            tmp_path = tmp.name
        
        try:
            result = self.validator._validate_pdf_content(tmp_path)
            assert result['errors'] == []
            assert len(result['warnings']) == 0
        finally:
            os.unlink(tmp_path)
    
    @patch('app.services.document_validator.pdfplumber.open')
    def test_validate_pdf_content_no_text(self, mock_pdfplumber):
        """Test PDF content validation with no extractable text."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4\n%test')
            tmp_path = tmp.name
        
        try:
            result = self.validator._validate_pdf_content(tmp_path)
            assert any('no extractable text' in warning for warning in result['warnings'])
        finally:
            os.unlink(tmp_path)
    
    @patch('app.services.document_validator.Document')
    def test_validate_document_content_docx(self, mock_document):
        """Test DOCX content validation."""
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = "This is a test document with content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            result = self.validator._validate_document_content(tmp_path, 'docx')
            assert result['errors'] == []
        finally:
            os.unlink(tmp_path)
    
    @patch('app.services.document_validator.magic.from_file')
    def test_validate_file_success(self, mock_magic):
        """Test successful file validation."""
        mock_magic.return_value = 'application/pdf'
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4\n' + b'x' * 1000)  # Valid PDF with content
            tmp_path = tmp.name
        
        try:
            with patch.object(self.validator, '_validate_pdf_content') as mock_validate:
                mock_validate.return_value = {'errors': [], 'warnings': []}
                
                result = self.validator.validate_file(tmp_path, 'test.pdf')
                
                assert result['is_valid'] is True
                assert result['file_type'] == 'pdf'
                assert result['mime_type'] == 'application/pdf'
                assert result['file_size'] > 0
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_content_error_handling(self):
        """Test error handling in file content validation."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'invalid content')
            tmp_path = tmp.name
        
        try:
            result = self.validator._validate_file_content(tmp_path, 'pdf')
            assert len(result['errors']) > 0
        finally:
            os.unlink(tmp_path)
