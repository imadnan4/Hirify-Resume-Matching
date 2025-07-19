import pytest
import numpy as np
from app.services.similarity_engine import SimilarityEngine


class TestSimilarityEngine:
    """Test suite for the SimilarityEngine class"""
    
    @pytest.fixture(scope='class')
    def engine(self):
        """Create similarity engine instance for testing"""
        return SimilarityEngine(use_gpu=False)
    
    def test_tfidf_similarity_identical_texts(self, engine):
        """Test TF-IDF similarity for identical texts"""
        text1 = "This is a test document about machine learning and data science."
        text2 = "This is a test document about machine learning and data science."
        
        similarity = engine.calculate_tfidf_similarity(text1, text2)
        
        assert similarity == 1.0, "Identical texts should have similarity of 1.0"
    
    def test_tfidf_similarity_different_texts(self, engine):
        """Test TF-IDF similarity for different texts"""
        text1 = "This is about machine learning and artificial intelligence."
        text2 = "This document discusses cooking recipes and kitchen techniques."
        
        similarity = engine.calculate_tfidf_similarity(text1, text2)
        
        assert 0.0 <= similarity <= 1.0, "Similarity should be between 0 and 1"
        assert similarity < 0.5, "Very different texts should have low similarity"
    
    def test_tfidf_similarity_similar_texts(self, engine):
        """Test TF-IDF similarity for similar texts"""
        text1 = "Python programming language machine learning data science"
        text2 = "Python programming artificial intelligence machine learning"
        
        similarity = engine.calculate_tfidf_similarity(text1, text2)
        
        assert similarity > 0.5, "Similar texts should have high similarity"
    
    def test_tfidf_similarity_empty_texts(self, engine):
        """Test TF-IDF similarity with empty texts"""
        text1 = ""
        text2 = "This is a test document."
        
        similarity = engine.calculate_tfidf_similarity(text1, text2)
        
        assert similarity == 0.0, "Empty text should have similarity of 0.0"
    
    def test_semantic_similarity(self, engine):
        """Test semantic similarity calculation"""
        text1 = "Software engineer with Python experience"
        text2 = "Python developer with programming skills"
        
        similarity = engine.calculate_semantic_similarity(text1, text2)
        
        assert 0.0 <= similarity <= 1.0, "Similarity should be between 0 and 1"
        assert similarity > 0.3, "Semantically similar texts should have decent similarity"
    
    def test_batch_similarity_calculation(self, engine):
        """Test batch similarity calculation"""
        reference_text = "Python machine learning engineer"
        candidate_texts = [
            "Python developer with ML experience",
            "Java programmer with database skills",
            "Machine learning specialist using Python",
            "Frontend developer with React knowledge"
        ]
        
        similarities = engine.batch_similarity_calculation(candidate_texts, reference_text)
        
        assert len(similarities) == len(candidate_texts), "Should return similarity for each candidate"
        assert all(0.0 <= sim <= 1.0 for sim in similarities), "All similarities should be between 0 and 1"
        
        # The first and third candidates should be more similar to the reference
        assert similarities[0] > similarities[1], "ML Python dev should be more similar than Java dev"
        assert similarities[2] > similarities[3], "ML specialist should be more similar than frontend dev"
    
    def test_find_most_similar(self, engine):
        """Test finding most similar texts"""
        query_text = "Senior Python developer with Django experience"
        candidate_texts = [
            "Junior Python developer with Flask experience",
            "Senior Java developer with Spring experience", 
            "Python developer with Django and REST API experience",
            "Frontend developer with React and JavaScript",
            "Data scientist with Python and machine learning"
        ]
        
        results = engine.find_most_similar(query_text, candidate_texts, top_k=3)
        
        assert len(results) == 3, "Should return top 3 results"
        assert all(isinstance(result, tuple) and len(result) == 2 for result in results), "Each result should be (index, similarity) tuple"
        assert all(0 <= result[0] < len(candidate_texts) for result in results), "Indices should be valid"
        assert all(0.0 <= result[1] <= 1.0 for result in results), "Similarities should be between 0 and 1"
        
        # Results should be sorted by similarity (descending)
        similarities = [result[1] for result in results]
        assert similarities == sorted(similarities, reverse=True), "Results should be sorted by similarity"
    
    def test_combined_similarity(self, engine):
        """Test combined similarity calculation"""
        text1 = "Machine learning engineer with Python expertise"
        text2 = "Python developer specializing in AI and ML"
        
        results = engine.calculate_combined_similarity(text1, text2)
        
        assert isinstance(results, dict), "Should return dictionary of results"
        assert 'combined' in results, "Should include combined score"
        assert 0.0 <= results['combined'] <= 1.0, "Combined score should be between 0 and 1"
        
        # Check that individual methods are included
        expected_methods = ['tfidf']  # At minimum, TF-IDF should be available
        for method in expected_methods:
            if method in results:
                assert 0.0 <= results[method] <= 1.0, f"{method} score should be between 0 and 1"
    
    def test_text_preprocessing(self, engine):
        """Test text preprocessing"""
        text = "  This is a TEST document with EXTRA    spaces and Mixed-Case  "
        processed = engine.preprocess_text(text)
        
        assert processed != text, "Text should be processed"
        assert "  " not in processed, "Extra spaces should be removed"
        assert processed.islower(), "Text should be lowercase"
    
    def test_cache_functionality(self, engine):
        """Test embedding cache functionality"""
        # Clear cache first
        engine.clear_cache()
        
        cache_info = engine.get_cache_info()
        assert cache_info['cache_size'] == 0, "Cache should be empty initially"
        
        # Calculate similarity to populate cache
        text1 = "Test document for caching"
        text2 = "Another test document"
        
        similarity1 = engine.calculate_semantic_similarity(text1, text2)
        
        # Cache should now have entries
        cache_info = engine.get_cache_info()
        assert cache_info['cache_size'] > 0, "Cache should have entries after calculation"
        
        # Calculate again - should use cache
        similarity2 = engine.calculate_semantic_similarity(text1, text2)
        
        assert similarity1 == similarity2, "Cached results should be identical"
    
    def test_benchmark_methods(self, engine):
        """Test benchmarking of different similarity methods"""
        text1 = "Python machine learning engineer with 5 years experience"
        text2 = "ML engineer specializing in Python and data science"
        
        benchmark_results = engine.benchmark_methods(text1, text2)
        
        assert isinstance(benchmark_results, dict), "Should return dictionary of results"
        
        # Check that at least TF-IDF is benchmarked
        assert 'tfidf' in benchmark_results, "Should benchmark TF-IDF method"
        
        tfidf_result = benchmark_results['tfidf']
        assert 'similarity' in tfidf_result, "Should include similarity score"
        assert 'execution_time' in tfidf_result, "Should include execution time"
        assert 'success' in tfidf_result, "Should include success status"
        
        assert tfidf_result['success'] is True, "TF-IDF should succeed"
        assert 0.0 <= tfidf_result['similarity'] <= 1.0, "Similarity should be between 0 and 1"
        assert tfidf_result['execution_time'] > 0, "Execution time should be positive"
    
    def test_batch_tfidf_similarity(self, engine):
        """Test batch TF-IDF similarity calculation"""
        texts = [
            "Python machine learning engineer",
            "Java software developer",
            "Data scientist with Python",
            "Frontend React developer"
        ]
        
        similarity_matrix = engine.calculate_tfidf_similarity_batch(texts)
        
        assert similarity_matrix.shape == (len(texts), len(texts)), "Matrix should be NxN"
        assert np.allclose(np.diag(similarity_matrix), 1.0), "Diagonal should be 1.0 (self-similarity)"
        assert np.allclose(similarity_matrix, similarity_matrix.T), "Matrix should be symmetric"
        
        # Check that similar texts have higher similarity
        assert similarity_matrix[0, 2] > similarity_matrix[0, 1], "Python ML engineer should be more similar to Python data scientist than Java dev"
    
    def test_empty_candidate_texts(self, engine):
        """Test handling of empty candidate texts list"""
        query_text = "Python developer"
        candidate_texts = []
        
        results = engine.find_most_similar(query_text, candidate_texts, top_k=5)
        
        assert len(results) == 0, "Should return empty list for empty candidates"
    
    def test_similarity_bounds(self, engine):
        """Test that similarity scores are always within valid bounds"""
        test_cases = [
            ("", ""),  # Empty texts
            ("a", "b"),  # Very short texts
            ("python programming", "java development"),  # Different technologies
            ("machine learning", "artificial intelligence"),  # Similar concepts
            ("the quick brown fox", "the lazy dog sleeps")  # Different content
        ]
        
        for text1, text2 in test_cases:
            similarity = engine.calculate_semantic_similarity(text1, text2)
            assert 0.0 <= similarity <= 1.0, f"Similarity {similarity} not in bounds for texts: '{text1}' vs '{text2}'"
    
    def test_custom_weights(self, engine):
        """Test combined similarity with custom weights"""
        text1 = "Python machine learning engineer"
        text2 = "ML engineer with Python expertise"
        
        custom_weights = {
            'tfidf': 0.7,
            'sentence_transformer': 0.3
        }
        
        results = engine.calculate_combined_similarity(text1, text2, weights=custom_weights)
        
        assert 'combined' in results, "Should include combined score"
        assert 0.0 <= results['combined'] <= 1.0, "Combined score should be between 0 and 1"
        
        # Only methods with non-zero weights should be included
        for method in custom_weights:
            if custom_weights[method] > 0:
                assert method in results, f"Method {method} should be in results"
