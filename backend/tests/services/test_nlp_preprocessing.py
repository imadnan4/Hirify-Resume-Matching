import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.nlp_preprocessing import NLPPreprocessingPipeline
from app.services.nlp_advanced import AdvancedNLPPipeline, ProcessingResult
from app.services.text_preprocessing import TextPreprocessingService, TextPreprocessingResult
from app.services.nltk_setup import download_nltk_data, check_nltk_data


class TestNLPPreprocessingPipeline(unittest.TestCase):
    """Test basic NLP preprocessing pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('app.services.nlp_preprocessing.stopwords') as mock_stopwords:
            mock_stopwords.words.return_value = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            self.pipeline = NLPPreprocessingPipeline()

    def test_clean_text(self):
        """Test text cleaning functionality."""
        test_text = "This    is   a   test   text   with   multiple   spaces."
        cleaned = self.pipeline.clean_text(test_text)
        
        # Should normalize whitespace
        self.assertNotIn('   ', cleaned)
        self.assertIn('This is a test text', cleaned)

    @patch('app.services.nlp_preprocessing.word_tokenize')
    @patch('app.services.nlp_preprocessing.sent_tokenize')
    def test_tokenize_text(self, mock_sent_tokenize, mock_word_tokenize):
        """Test text tokenization."""
        mock_sent_tokenize.return_value = ['This is a test.', 'Another sentence.']
        mock_word_tokenize.return_value = ['This', 'is', 'a', 'test', '.', 'Another', 'sentence', '.']
        
        sentences, words = self.pipeline.tokenize_text("This is a test. Another sentence.")
        
        self.assertEqual(len(sentences), 2)
        self.assertEqual(len(words), 8)
        self.assertEqual(sentences[0], 'This is a test.')

    def test_remove_stopwords(self):
        """Test stopword removal."""
        words = ['This', 'is', 'a', 'test', 'sentence', 'with', 'some', 'words']
        filtered = self.pipeline.remove_stopwords(words)
        
        # Should remove common stopwords
        self.assertNotIn('is', filtered)
        self.assertNotIn('a', filtered)
        self.assertIn('test', filtered)
        self.assertIn('sentence', filtered)

    @patch('app.services.nlp_preprocessing.WordNetLemmatizer')
    def test_lemmatize_words(self, mock_lemmatizer_class):
        """Test word lemmatization."""
        mock_lemmatizer = Mock()
        mock_lemmatizer.lemmatize.side_effect = lambda word: word.lower()
        mock_lemmatizer_class.return_value = mock_lemmatizer
        
        pipeline = NLPPreprocessingPipeline()
        words = ['running', 'ran', 'runs']
        lemmatized = pipeline.lemmatize_words(words)
        
        self.assertEqual(len(lemmatized), 3)
        mock_lemmatizer.lemmatize.assert_called()

    def test_process_text_integration(self):
        """Test complete text processing pipeline."""
        test_text = "This is a test document with multiple sentences. It contains various words."
        
        with patch('app.services.nlp_preprocessing.sent_tokenize') as mock_sent, \
             patch('app.services.nlp_preprocessing.word_tokenize') as mock_word:
            
            mock_sent.return_value = ['This is a test document.', 'It contains various words.']
            mock_word.return_value = ['This', 'is', 'test', 'document', 'contains', 'various', 'words']
            
            result = self.pipeline.process_text(test_text)
            
            self.assertIn('cleaned_text', result)
            self.assertIn('sentences', result)
            self.assertIn('words', result)
            self.assertIsInstance(result['sentences'], list)
            self.assertIsInstance(result['words'], list)


class TestAdvancedNLPPipeline(unittest.TestCase):
    """Test advanced NLP preprocessing pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock spaCy model loading
        with patch('app.services.nlp_advanced.spacy.load') as mock_spacy_load:
            mock_nlp = Mock()
            mock_spacy_load.return_value = mock_nlp
            
            with patch('app.services.nlp_advanced.stopwords') as mock_stopwords:
                mock_stopwords.words.return_value = ['the', 'a', 'an']
                self.pipeline = AdvancedNLPPipeline()

    def test_clean_text(self):
        """Test advanced text cleaning."""
        test_text = "This  is  a  test  with  multiple  spaces  and  special  chars!!!"
        cleaned = self.pipeline.clean_text(test_text)
        
        self.assertNotIn('  ', cleaned)
        self.assertIn('test', cleaned)

    @patch('app.services.nlp_advanced.spacy')
    def test_extract_entities(self, mock_spacy):
        """Test named entity extraction."""
        # Mock spaCy document and entities
        mock_doc = Mock()
        mock_entity = Mock()
        mock_entity.text = "John Doe"
        mock_entity.label_ = "PERSON"
        mock_entity.start_char = 0
        mock_entity.end_char = 8
        mock_doc.ents = [mock_entity]
        
        mock_spacy.explain.return_value = "Person"
        self.pipeline.nlp.return_value = mock_doc
        
        entities = self.pipeline.extract_entities("John Doe works at Google")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]['text'], "John Doe")
        self.assertEqual(entities[0]['label'], "PERSON")

    def test_extract_keywords(self):
        """Test keyword extraction."""
        # Mock spaCy document
        mock_doc = Mock()
        mock_token1 = Mock()
        mock_token1.lemma_ = "software"
        mock_token1.is_stop = False
        mock_token1.is_punct = False
        mock_token1.is_space = False
        mock_token1.text = "software"
        mock_token1.pos_ = "NOUN"
        
        mock_token2 = Mock()
        mock_token2.lemma_ = "engineer"
        mock_token2.is_stop = False
        mock_token2.is_punct = False
        mock_token2.is_space = False
        mock_token2.text = "engineer"
        mock_token2.pos_ = "NOUN"
        
        mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2]))
        self.pipeline.nlp.return_value = mock_doc
        
        keywords = self.pipeline.extract_keywords("software engineer")
        
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) <= 10)  # Should respect top_n parameter

    def test_extract_contact_info(self):
        """Test contact information extraction."""
        test_text = "Contact: john.doe@example.com, phone: 123-456-7890"
        
        contact_info = self.pipeline.extract_contact_info(test_text)
        
        self.assertIn('emails', contact_info)
        self.assertIn('phones', contact_info)
        self.assertIn('urls', contact_info)
        self.assertIn('addresses', contact_info)

    def test_extract_dates(self):
        """Test date extraction."""
        # Mock spaCy document with date entities
        mock_doc = Mock()
        mock_entity = Mock()
        mock_entity.text = "2020-2023"
        mock_entity.label_ = "DATE"
        mock_entity.start_char = 0
        mock_entity.end_char = 9
        mock_doc.ents = [mock_entity]
        
        self.pipeline.nlp.return_value = mock_doc
        
        dates = self.pipeline.extract_dates("Worked from 2020-2023")
        
        self.assertEqual(len(dates), 1)
        self.assertEqual(dates[0]['text'], "2020-2023")

    def test_extract_organizations(self):
        """Test organization extraction."""
        # Mock spaCy document with organization entities
        mock_doc = Mock()
        mock_entity = Mock()
        mock_entity.text = "Google"
        mock_entity.label_ = "ORG"
        mock_doc.ents = [mock_entity]
        
        self.pipeline.nlp.return_value = mock_doc
        
        organizations = self.pipeline.extract_organizations("I work at Google")
        
        self.assertEqual(len(organizations), 1)
        self.assertEqual(organizations[0], "Google")

    def test_extract_skills_section(self):
        """Test skills section extraction."""
        test_text = """
        Skills:
        Python, Java, JavaScript
        Machine Learning, Data Analysis
        """
        
        skills = self.pipeline.extract_skills_section(test_text)
        
        self.assertIsInstance(skills, list)
        self.assertTrue(len(skills) > 0)


class TestTextPreprocessingService(unittest.TestCase):
    """Test comprehensive text preprocessing service."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock all dependencies
        with patch('app.services.text_preprocessing.check_nltk_data') as mock_check, \
             patch('app.services.text_preprocessing.NLPPreprocessingPipeline') as mock_basic, \
             patch('app.services.text_preprocessing.AdvancedNLPPipeline') as mock_advanced:
            
            mock_check.return_value = []  # No missing data
            self.service = TextPreprocessingService(ensure_nltk_data=False)

    def test_extract_sections(self):
        """Test section extraction from resume text."""
        test_text = """
        EXPERIENCE
        Software Engineer at Google
        2020-2023
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of California
        """
        
        sections = self.service._extract_sections(test_text)
        
        self.assertIn('experience', sections)
        self.assertIn('education', sections)

    def test_calculate_quality_metrics(self):
        """Test quality metrics calculation."""
        test_text = "This is a test resume with contact info: john@example.com"
        
        # Mock ProcessingResult
        mock_result = Mock()
        mock_result.entities = [{'text': 'John', 'label': 'PERSON'}] * 6  # More than 5 entities
        mock_result.keywords = ['skill'] * 11  # More than 10 keywords
        mock_result.statistics = {'lexical_diversity': 0.6}
        
        metrics = self.service._calculate_quality_metrics(test_text, mock_result)
        
        self.assertIn('completeness_score', metrics)
        self.assertIn('structure_score', metrics)
        self.assertIn('content_quality', metrics)
        self.assertIsInstance(metrics['completeness_score'], float)

    def test_estimate_experience_years(self):
        """Test experience years estimation."""
        dates = [
            {'text': '2020-2023'},
            {'text': '2018-2020'},
            {'text': '2016-2018'}
        ]
        
        years = self.service._estimate_experience_years(dates)
        self.assertIsInstance(years, int)
        self.assertGreaterEqual(years, 0)

    def test_estimate_education_level(self):
        """Test education level estimation."""
        education_text = "Bachelor of Science in Computer Science"
        level = self.service._estimate_education_level(education_text)
        self.assertEqual(level, 'bachelors')
        
        education_text = "Master of Business Administration"
        level = self.service._estimate_education_level(education_text)
        self.assertEqual(level, 'masters')
        
        education_text = "PhD in Computer Science"
        level = self.service._estimate_education_level(education_text)
        self.assertEqual(level, 'doctorate')

    def test_validate_preprocessing_setup(self):
        """Test preprocessing setup validation."""
        validation_results = self.service.validate_preprocessing_setup()
        
        self.assertIn('basic_nlp', validation_results)
        self.assertIn('advanced_nlp', validation_results)
        self.assertIn('nltk_data', validation_results)
        self.assertIsInstance(validation_results['basic_nlp'], bool)


class TestNLTKSetup(unittest.TestCase):
    """Test NLTK setup utilities."""

    @patch('app.services.nltk_setup.nltk.download')
    @patch('app.services.nltk_setup.nltk.data.find')
    def test_download_nltk_data(self, mock_find, mock_download):
        """Test NLTK data download."""
        mock_find.side_effect = LookupError("Not found")
        mock_download.return_value = True
        
        download_nltk_data()
        
        # Should attempt to download required datasets
        self.assertTrue(mock_download.called)

    @patch('app.services.nltk_setup.nltk.data.find')
    def test_check_nltk_data(self, mock_find):
        """Test NLTK data checking."""
        mock_find.side_effect = LookupError("Not found")
        
        missing = check_nltk_data()
        
        self.assertIsInstance(missing, list)
        self.assertTrue(len(missing) > 0)


if __name__ == '__main__':
    unittest.main()
