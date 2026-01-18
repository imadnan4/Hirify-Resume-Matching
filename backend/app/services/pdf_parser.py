"""
PDF text extraction service using pdfplumber with advanced features.
"""
import pdfplumber
import PyPDF2
from typing import Dict, List, Optional, Any
import logging
import re
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)


class PDFParsingError(Exception):
    """Custom exception for PDF parsing errors."""
    pass


class PDFParser:
    """Service for parsing PDF documents and extracting text content."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file with metadata and structure preservation.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict containing extracted text and metadata
            
        Raises:
            PDFParsingError: If PDF parsing fails
        """
        try:
            result = {
                'text': '',
                'pages': [],
                'metadata': {},
                'structure': {},
                'extraction_method': 'pdfplumber',
                'errors': [],
                'warnings': []
            }
            
            # First try with pdfplumber (preferred method)
            try:
                result = self._extract_with_pdfplumber(file_path)
                logger.info(f"Successfully extracted text from PDF using pdfplumber: {file_path}")
            except Exception as e:
                logger.warning(f"pdfplumber failed for {file_path}: {str(e)}")
                # Fallback to PyPDF2
                try:
                    result = self._extract_with_pypdf2(file_path)
                    result['extraction_method'] = 'pypdf2'
                    result['warnings'].append("Used fallback extraction method (PyPDF2)")
                    logger.info(f"Successfully extracted text from PDF using PyPDF2: {file_path}")
                except Exception as e2:
                    logger.error(f"Both extraction methods failed for {file_path}: {str(e2)}")
                    raise PDFParsingError(f"Failed to extract text from PDF: {str(e2)}")
            
            # Post-process the extracted text
            result = self._post_process_text(result)
            
            # Validate extraction quality
            self._validate_extraction_quality(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise PDFParsingError(f"PDF parsing failed: {str(e)}")
    
    def _extract_with_pdfplumber(self, file_path: str) -> Dict[str, Any]:
        """Extract text using pdfplumber with layout preservation."""
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'structure': {},
            'extraction_method': 'pdfplumber',
            'errors': [],
            'warnings': []
        }
        
        with pdfplumber.open(file_path) as pdf:
            # Extract metadata
            result['metadata'] = self._extract_metadata(pdf)
            
            # Extract text from each page
            all_text = []
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # Extract text with layout preservation
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)
                        
                        # Extract page-specific information
                        page_info = {
                            'page_number': page_num,
                            'text': page_text,
                            'char_count': len(page_text),
                            'word_count': len(page_text.split()),
                            'tables': [],
                            'images': []
                        }
                        
                        # Extract tables if present
                        tables = page.extract_tables()
                        if tables:
                            page_info['tables'] = self._process_tables(tables)
                        
                        # Get image information
                        if hasattr(page, 'images') and page.images:
                            page_info['images'] = [{'width': img.get('width', 0), 
                                                  'height': img.get('height', 0)} 
                                                 for img in page.images]
                        
                        result['pages'].append(page_info)
                    
                except Exception as e:
                    result['errors'].append(f"Error extracting page {page_num}: {str(e)}")
                    logger.warning(f"Error extracting page {page_num} from {file_path}: {str(e)}")
            
            # Combine all text
            result['text'] = '\n\n'.join(all_text)
            
            # Extract document structure
            result['structure'] = self._analyze_document_structure(result['text'])
        
        return result
    
    def _extract_with_pypdf2(self, file_path: str) -> Dict[str, Any]:
        """Extract text using PyPDF2 as fallback method."""
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'structure': {},
            'extraction_method': 'pypdf2',
            'errors': [],
            'warnings': []
        }
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            if pdf_reader.metadata:
                result['metadata'] = {
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                    'modification_date': str(pdf_reader.metadata.get('/ModDate', '')),
                    'pages': len(pdf_reader.pages)
                }
            
            # Extract text from each page
            all_text = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)
                        
                        page_info = {
                            'page_number': page_num,
                            'text': page_text,
                            'char_count': len(page_text),
                            'word_count': len(page_text.split()),
                            'tables': [],
                            'images': []
                        }
                        
                        result['pages'].append(page_info)
                
                except Exception as e:
                    result['errors'].append(f"Error extracting page {page_num}: {str(e)}")
                    logger.warning(f"Error extracting page {page_num} from {file_path}: {str(e)}")
            
            # Combine all text
            result['text'] = '\n\n'.join(all_text)
            
            # Extract document structure
            result['structure'] = self._analyze_document_structure(result['text'])
        
        return result
    
    def _extract_metadata(self, pdf) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        metadata = {
            'pages': len(pdf.pages),
            'title': '',
            'author': '',
            'creator': '',
            'producer': '',
            'creation_date': '',
            'modification_date': ''
        }
        
        try:
            if hasattr(pdf, 'metadata') and pdf.metadata:
                metadata.update({
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', ''),
                    'creation_date': str(pdf.metadata.get('CreationDate', '')),
                    'modification_date': str(pdf.metadata.get('ModDate', ''))
                })
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {str(e)}")
        
        return metadata
    
    def _process_tables(self, tables: List[List[List[str]]]) -> List[Dict[str, Any]]:
        """Process extracted tables into structured format."""
        processed_tables = []
        
        for i, table in enumerate(tables):
            if not table:
                continue
                
            table_info = {
                'table_number': i + 1,
                'rows': len(table),
                'columns': len(table[0]) if table else 0,
                'data': table,
                'headers': table[0] if table else []
            }
            
            processed_tables.append(table_info)
        
        return processed_tables
    
    def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure and identify sections."""
        structure = {
            'sections': [],
            'has_contact_info': False,
            'has_experience': False,
            'has_education': False,
            'has_skills': False,
            'estimated_sections': []
        }
        
        if not text:
            return structure
        
        # Common section patterns in resumes
        section_patterns = {
            'contact': r'(?i)(contact|phone|email|address|linkedin)',
            'summary': r'(?i)(summary|profile|objective|about)',
            'experience': r'(?i)(experience|employment|work\s+history|professional)',
            'education': r'(?i)(education|academic|degree|university|college)',
            'skills': r'(?i)(skills|technical|competencies|abilities)',
            'projects': r'(?i)(projects|portfolio)',
            'certifications': r'(?i)(certifications|certificates|licenses)',
            'achievements': r'(?i)(achievements|awards|accomplishments)'
        }
        
        # Analyze text for different sections
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, text):
                structure[f'has_{section_name}'] = True
                structure['estimated_sections'].append(section_name)
        
        # Try to identify section boundaries
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like a section header
            if self._is_section_header(line):
                if current_section:
                    structure['sections'].append(current_section)
                
                current_section = {
                    'title': line,
                    'content': '',
                    'line_count': 0
                }
            elif current_section:
                current_section['content'] += line + '\n'
                current_section['line_count'] += 1
        
        # Add the last section
        if current_section:
            structure['sections'].append(current_section)
        
        return structure
    
    def _is_section_header(self, line: str) -> bool:
        """Determine if a line looks like a section header."""
        # Simple heuristics for section headers
        if len(line) > 50:  # Too long to be a header
            return False
        
        # Check for common header patterns
        header_patterns = [
            r'^[A-Z\s]+$',  # All caps
            r'^[A-Za-z\s]+:$',  # Ends with colon
            r'^\d+\.\s+[A-Za-z]',  # Numbered section
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$'  # Title case
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _post_process_text(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process extracted text to improve quality."""
        if not result['text']:
            return result
        
        # Clean up text
        text = result['text']
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Replace multiple newlines with double newline
        text = re.sub(r' +', ' ', text)  # Replace multiple spaces with single space
        
        # Fix common extraction issues
        text = text.replace('\u2022', '•')  # Replace bullet points
        text = text.replace('\u2013', '-')  # Replace en dash
        text = text.replace('\u2014', '--')  # Replace em dash
        
        # Remove page numbers and headers/footers (simple approach)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that look like page numbers
            if re.match(r'^\d+$', line) or re.match(r'^Page\s+\d+', line):
                continue
            cleaned_lines.append(line)
        
        result['text'] = '\n'.join(cleaned_lines)
        
        # Update statistics
        result['statistics'] = {
            'total_characters': len(result['text']),
            'total_words': len(result['text'].split()),
            'total_lines': len(result['text'].split('\n')),
            'average_words_per_page': len(result['text'].split()) / len(result['pages']) if result['pages'] else 0
        }
        
        return result
    
    def _validate_extraction_quality(self, result: Dict[str, Any]) -> None:
        """Validate the quality of text extraction."""
        if not result['text']:
            result['warnings'].append("No text was extracted from the PDF")
            return
        
        text = result['text']
        
        # Check for minimum content
        if len(text.split()) < 10:
            result['warnings'].append("Very little text was extracted - document may be image-based")
        
        # Check for garbled text (high ratio of non-alphabetic characters)
        alpha_chars = sum(1 for char in text if char.isalpha())
        total_chars = len(text.replace(' ', '').replace('\n', ''))
        
        if total_chars > 0 and alpha_chars / total_chars < 0.7:
            result['warnings'].append("Extracted text may contain garbled characters")
        
        # Check for reasonable structure
        if '\n' not in text and len(text) > 100:
            result['warnings'].append("Text appears to lack proper line breaks")
        
        logger.info(f"Text extraction quality check completed. Characters: {len(text)}, Words: {len(text.split())}")
    
    def is_pdf_file(self, file_path: str) -> bool:
        """Check if file is a valid PDF."""
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages) > 0
        except:
            return False
    
    def get_page_count(self, file_path: str) -> int:
        """Get the number of pages in a PDF."""
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except:
            return 0
