"""
Semantic Skills Extractor for Hirify
Uses embeddings for skill matching instead of hardcoded taxonomies.
"""
import re
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass
import logging

from .nlp_service import nlp_service
from .embedding_engine import SimilarityEngine

logger = logging.getLogger(__name__)


@dataclass
class ExtractedSkill:
    """Represents an extracted skill"""
    name: str
    category: str  # technical, soft, certification
    confidence: float
    source_text: str  # Original text where found
    normalized_name: Optional[str] = None  # Standardized skill name


class SemanticSkillsExtractor:
    """
    Skills extractor using semantic embeddings.
    
    Key improvements over keyword matching:
    - "React" matches "React.js", "ReactJS" automatically
    - "ML" matches "Machine Learning"
    - No need for manual alias lists
    """
    
    # Core skill categories with representative examples
    # These are used to help classify skills, not for exact matching
    SKILL_CATEGORIES = {
        "programming_languages": [
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", 
            "TypeScript", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R"
        ],
        "frameworks": [
            "React", "Angular", "Vue.js", "Django", "Flask", "Spring Boot",
            "Express.js", "FastAPI", "Rails", "Laravel", "ASP.NET"
        ],
        "databases": [
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
            "SQLite", "Oracle", "SQL Server", "DynamoDB", "Cassandra"
        ],
        "cloud_devops": [
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes",
            "Jenkins", "GitHub Actions", "Terraform", "Ansible", "CI/CD"
        ],
        "data_ml": [
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "Pandas", "NumPy", "Scikit-learn", "Data Analysis", "NLP"
        ],
        "soft_skills": [
            "Leadership", "Communication", "Problem Solving", "Teamwork",
            "Project Management", "Agile", "Scrum", "Time Management"
        ],
        "certifications": [
            "AWS Certified", "Azure Certified", "PMP", "Scrum Master",
            "CISSP", "Google Cloud Certified", "Kubernetes Certified"
        ]
    }
    
    # Skill extraction patterns
    SKILL_PATTERNS = [
        # Common resume skill section patterns
        r'(?:skills?|technologies?|expertise|proficient in|experienced with|knowledge of)[:\s]+([^.]+)',
        r'(?:technical skills?)[:\s]+([^.]+)',
        # List patterns
        r'•\s*([A-Za-z0-9\+\#\.\s]{2,30})',
        r'-\s*([A-Za-z0-9\+\#\.\s]{2,30})',
    ]
    
    def __init__(self, similarity_threshold: float = 0.75):
        """
        Initialize the extractor.
        
        Args:
            similarity_threshold: Minimum similarity score for skill matching
        """
        self.similarity_threshold = similarity_threshold
        self.similarity_engine = SimilarityEngine()
        
        # Flatten all known skills for matching
        self._all_known_skills = []
        self._skill_to_category = {}
        for category, skills in self.SKILL_CATEGORIES.items():
            for skill in skills:
                self._all_known_skills.append(skill)
                self._skill_to_category[skill.lower()] = category
        
        # Pre-compute embeddings for known skills (lazy loaded)
        self._skill_embeddings = None
    
    def _load_skill_embeddings(self):
        """Lazy load skill embeddings"""
        if self._skill_embeddings is None:
            self._skill_embeddings = self.similarity_engine.get_embeddings_batch(
                self._all_known_skills
            )
    
    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extract skills from text using multiple methods.
        
        Args:
            text: Text to extract skills from (resume or job description)
            
        Returns:
            Dict with 'skills' list and 'summary'
        """
        if not text:
            return {"skills": [], "summary": self._empty_summary()}
        
        all_skills = []
        
        # Method 1: Extract using NLP keywords
        keywords = nlp_service.extract_keywords(text, top_n=50)
        for keyword in keywords:
            skill = self._match_skill(keyword)
            if skill:
                all_skills.append(skill)
        
        # Method 2: Extract from skill sections using patterns
        pattern_skills = self._extract_from_patterns(text)
        all_skills.extend(pattern_skills)
        
        # Method 3: Extract using NER entities
        entities = nlp_service.extract_entities(text)
        for entity in entities:
            if entity['label'] in ['ORG', 'PRODUCT']:
                skill = self._match_skill(entity['text'])
                if skill:
                    all_skills.append(skill)
        
        # Deduplicate and merge
        unique_skills = self._deduplicate_skills(all_skills)
        
        # Sort by confidence
        unique_skills.sort(key=lambda x: x.confidence, reverse=True)
        
        # Convert to dict format
        skills_list = [
            {
                "skill": s.name,
                "category": s.category,
                "confidence": s.confidence,
                "normalized": s.normalized_name or s.name
            }
            for s in unique_skills
        ]
        
        return {
            "skills": skills_list,
            "summary": self._create_summary(skills_list)
        }
    
    def _match_skill(self, text: str) -> Optional[ExtractedSkill]:
        """
        Match text to a known skill using semantic similarity.
        """
        if not text or len(text) < 2:
            return None
        
        text_clean = text.strip().lower()
        
        # Quick exact match check first
        if text_clean in self._skill_to_category:
            return ExtractedSkill(
                name=text,
                category=self._skill_to_category[text_clean],
                confidence=1.0,
                source_text=text,
                normalized_name=text_clean.title()
            )
        
        # Semantic matching
        self._load_skill_embeddings()
        
        text_embedding = self.similarity_engine.get_embedding(text)
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        similarities = cosine_similarity(
            text_embedding.reshape(1, -1),
            self._skill_embeddings
        )[0]
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        if best_score >= self.similarity_threshold:
            matched_skill = self._all_known_skills[best_idx]
            return ExtractedSkill(
                name=text,
                category=self._skill_to_category.get(matched_skill.lower(), "technical"),
                confidence=float(best_score),
                source_text=text,
                normalized_name=matched_skill
            )
        
        return None
    
    def _extract_from_patterns(self, text: str) -> List[ExtractedSkill]:
        """Extract skills using regex patterns"""
        skills = []
        
        for pattern in self.SKILL_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split on common delimiters
                items = re.split(r'[,;|/]', match)
                for item in items:
                    item = item.strip()
                    if 2 <= len(item) <= 50:
                        skill = self._match_skill(item)
                        if skill:
                            skills.append(skill)
        
        return skills
    
    def _deduplicate_skills(self, skills: List[ExtractedSkill]) -> List[ExtractedSkill]:
        """Remove duplicate skills, keeping highest confidence"""
        seen = {}
        for skill in skills:
            key = (skill.normalized_name or skill.name).lower()
            if key not in seen or skill.confidence > seen[key].confidence:
                seen[key] = skill
        return list(seen.values())
    
    def _create_summary(self, skills: List[Dict]) -> Dict[str, int]:
        """Create summary of extracted skills"""
        summary = {
            "total": len(skills),
            "technical": 0,
            "soft": 0,
            "certifications": 0,
            "by_category": {}
        }
        
        for skill in skills:
            category = skill.get("category", "technical")
            
            if category in ["soft_skills"]:
                summary["soft"] += 1
            elif category in ["certifications"]:
                summary["certifications"] += 1
            else:
                summary["technical"] += 1
            
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1
        
        return summary
    
    def _empty_summary(self) -> Dict[str, int]:
        """Return empty summary"""
        return {"total": 0, "technical": 0, "soft": 0, "certifications": 0}
    
    def match_skills(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Match skills between resume and job using semantic similarity.
        
        This is the key improvement: "React" will match "React.js" automatically.
        """
        return self.similarity_engine.match_skills_semantic(
            resume_skills,
            job_skills,
            threshold=self.similarity_threshold
        )
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """Get available skill categories"""
        return self.SKILL_CATEGORIES.copy()


# Create singleton instance
semantic_skills_extractor = SemanticSkillsExtractor()
