import pytest
from app.services.skills_extractor import SkillsExtractor


class TestSkillsExtractor:
    """Test suite for the SkillsExtractor class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.extractor = SkillsExtractor()
        
    def test_extract_technical_skills(self):
        """Test extraction of technical skills"""
        text = "I have 5 years of experience with Python, JavaScript, and React. I also know Docker and AWS."
        result = self.extractor.extract_skills(text)
        
        assert result["summary"]["technical"] > 0
        skill_names = [skill["skill"] for skill in result["skills"]]
        assert "python" in skill_names
        assert "javascript" in skill_names
        assert "react" in skill_names
        assert "docker" in skill_names
        assert "aws" in skill_names
        
    def test_extract_soft_skills(self):
        """Test extraction of soft skills"""
        text = "I have strong leadership skills and excellent communication abilities. I work well in teams."
        result = self.extractor.extract_skills(text)
        
        assert result["summary"]["soft"] > 0
        skill_names = [skill["skill"] for skill in result["skills"]]
        assert "leadership" in skill_names
        assert "communication" in skill_names
        assert "teamwork" in skill_names
        
    def test_extract_certifications(self):
        """Test extraction of certifications"""
        text = "I am AWS Certified and have a PMP certification. I also have a Scrum Master certification."
        result = self.extractor.extract_skills(text)
        
        assert result["summary"]["certifications"] > 0
        skill_names = [skill["skill"] for skill in result["skills"]]
        assert "aws certified" in skill_names
        assert "pmp" in skill_names
        assert "scrum master" in skill_names
        
    def test_skill_normalization(self):
        """Test that skill aliases are normalized correctly"""
        text = "I know JS, Python3, and React.js"
        result = self.extractor.extract_skills(text)
        
        skill_names = [skill["skill"] for skill in result["skills"]]
        assert "javascript" in skill_names
        assert "python" in skill_names
        assert "react" in skill_names
        
    def test_confidence_scoring(self):
        """Test that confidence scores are calculated correctly"""
        text = "Python Python Python JavaScript"
        result = self.extractor.extract_skills(text)
        
        python_skill = next(skill for skill in result["skills"] if skill["skill"] == "python")
        js_skill = next(skill for skill in result["skills"] if skill["skill"] == "javascript")
        
        # Python should have higher confidence due to multiple occurrences
        assert python_skill["confidence"] > js_skill["confidence"]
        
    def test_empty_text(self):
        """Test handling of empty text"""
        result = self.extractor.extract_skills("")
        
        assert result["summary"]["total"] == 0
        assert len(result["skills"]) == 0
        
    def test_fuzzy_matching(self):
        """Test fuzzy matching functionality"""
        matches = self.extractor.fuzzy_match_skills("javascrpit", threshold=0.7)
        
        assert len(matches) > 0
        assert "javascript" in matches
        
    def test_get_skill_categories(self):
        """Test getting skill categories"""
        categories = self.extractor.get_skill_categories()
        
        assert "technical_skills" in categories
        assert "soft_skills" in categories
        assert "certifications" in categories
        
        assert len(categories["technical_skills"]) > 0
        assert len(categories["soft_skills"]) > 0
        assert len(categories["certifications"]) > 0
        
    def test_duplicate_removal(self):
        """Test that duplicate skills are removed"""
        text = "Python python PYTHON JavaScript js"
        result = self.extractor.extract_skills(text)
        
        skill_names = [skill["skill"] for skill in result["skills"]]
        python_count = skill_names.count("python")
        javascript_count = skill_names.count("javascript")
        
        # Should only have one instance of each skill
        assert python_count == 1
        assert javascript_count == 1
        
    def test_minimum_confidence_threshold(self):
        """Test filtering by minimum confidence threshold"""
        text = "I have some experience with obscure_technology_xyz"
        result = self.extractor.extract_skills(text, min_confidence=0.9)
        
        # Should filter out low-confidence skills
        for skill in result["skills"]:
            assert skill["confidence"] >= 0.9
            
    def test_context_based_confidence_boost(self):
        """Test that skills in specific sections get confidence boost"""
        text = "Skills: Python, JavaScript, React"
        result = self.extractor.extract_skills(text)
        
        # Skills should have higher confidence when in "Skills" section
        for skill in result["skills"]:
            assert skill["confidence"] > 0.8
            
    def test_regex_pattern_matching(self):
        """Test regex pattern matching"""
        text = "I have experience with C++ and C#"
        result = self.extractor.extract_skills(text)
        
        skill_names = [skill["skill"] for skill in result["skills"]]
        assert "c++" in skill_names
        assert "c#" in skill_names
        
    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive"""
        text = "PYTHON JavaScript ReAcT"
        result = self.extractor.extract_skills(text)
        
        skill_names = [skill["skill"] for skill in result["skills"]]
        assert "python" in skill_names
        assert "javascript" in skill_names
        assert "react" in skill_names
