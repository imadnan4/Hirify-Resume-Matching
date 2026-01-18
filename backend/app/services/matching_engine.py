"""
Simplified Matching Service for Hirify

This service handles resume-job matching using semantic embeddings.
Key improvements:
1. Uses embeddings as primary matching method (not keyword matching)
2. Cleaner, more maintainable code structure
3. Better separation of concerns
"""
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import re
import logging

from .embedding_engine import SimilarityEngine
from .semantic_skills import SemanticSkillsExtractor
from .nlp_service import nlp_service

logger = logging.getLogger(__name__)


@dataclass
class MatchScore:
    """Match score breakdown"""
    overall: float
    semantic: float  # Embedding-based similarity
    skills: float
    experience: float
    education: float
    confidence: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "overall": round(self.overall, 3),
            "semantic": round(self.semantic, 3),
            "skills": round(self.skills, 3),
            "experience": round(self.experience, 3),
            "education": round(self.education, 3),
            "confidence": round(self.confidence, 3)
        }


@dataclass
class MatchResult:
    """Complete match result"""
    resume_id: str
    job_id: str
    score: MatchScore
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    skill_details: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "resume_id": self.resume_id,
            "job_id": self.job_id,
            "scores": self.score.to_dict(),
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "skill_details": self.skill_details,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat()
        }


class MatchingEngine:
    """
    Intelligent resume-job matching engine using SEMANTIC EMBEDDINGS.
    
    Primary matching is done via Sentence Transformer embeddings comparing
    the FULL text of resume vs job description. This captures overall fit
    including context that keyword matching misses.
    
    Scoring approach:
    - Semantic similarity (embedding-based): 60% - THE MAIN DRIVER
    - Skills overlap (also semantic): 25% 
    - Experience relevance: 10%
    - Education relevance: 5%
    """
    
    # Scoring weights - semantic is primary
    WEIGHTS = {
        "semantic": 0.60,  # Main driver - compares full documents
        "skills": 0.25,    # Skills match (also semantic)
        "experience": 0.10,
        "education": 0.05
    }
    
    # Education level hierarchy
    EDUCATION_LEVELS = {
        "high school": 1, "diploma": 1,
        "associate": 2,
        "bachelor": 3, "bs": 3, "ba": 3,
        "master": 4, "ms": 4, "ma": 4,
        "mba": 4.5,
        "phd": 5, "doctorate": 5, "doctoral": 5
    }
    
    def __init__(self):
        self.similarity_engine = SimilarityEngine()
        self.skills_extractor = SemanticSkillsExtractor()
    
    def match(
        self,
        resume_text: str,
        job_text: str,
        resume_id: str = None,
        job_id: str = None,
        resume_data: Dict = None,
        job_data: Dict = None
    ) -> MatchResult:
        """
        Calculate match between a resume and job description.
        
        Args:
            resume_text: Full text of the resume
            job_text: Full text of the job description
            resume_id: Optional resume identifier
            job_id: Optional job identifier
            resume_data: Optional structured resume data
            job_data: Optional structured job data
            
        Returns:
            MatchResult with detailed scoring
        """
        # Generate IDs if not provided
        resume_id = resume_id or str(hash(resume_text[:100]))
        job_id = job_id or str(hash(job_text[:100]))
        
        # 1. Semantic similarity (embedding-based)
        semantic_score = self.similarity_engine.calculate_similarity(resume_text, job_text)
        
        # 2. Skills match
        skills_score, skill_details = self._calculate_skills_score(
            resume_text, job_text, resume_data, job_data
        )
        
        # 3. Experience match
        experience_score = self._calculate_experience_score(
            resume_text, job_text, resume_data, job_data
        )
        
        # 4. Education match
        education_score = self._calculate_education_score(
            resume_text, job_text, resume_data, job_data
        )
        
        # Calculate weighted overall score
        overall_score = (
            semantic_score * self.WEIGHTS["semantic"] +
            skills_score * self.WEIGHTS["skills"] +
            experience_score * self.WEIGHTS["experience"] +
            education_score * self.WEIGHTS["education"]
        )
        
        # The semantic score is the TRUTH - it uses full document embeddings
        # If semantic similarity is very low, the documents are not a match
        # No artificial inflation of scores
        if semantic_score < 0.3:
            # Very poor semantic match - cap overall to reflect reality
            overall_score = min(overall_score, semantic_score + 0.1)
        
        # Round to avoid floating point issues
        overall_score = round(overall_score, 4)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(
            resume_text, job_text, skill_details
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            overall_score, semantic_score, skills_score,
            experience_score, education_score, skill_details
        )
        
        return MatchResult(
            resume_id=resume_id,
            job_id=job_id,
            score=MatchScore(
                overall=overall_score,
                semantic=semantic_score,
                skills=skills_score,
                experience=experience_score,
                education=education_score,
                confidence=confidence
            ),
            matched_skills=skill_details.get("matched_skills", []),
            missing_skills=skill_details.get("missing_skills", []),
            skill_details=skill_details,
            explanation=explanation
        )
    
    def match_batch(
        self,
        job_text: str,
        resume_texts: List[str],
        job_id: str = None
    ) -> List[MatchResult]:
        """
        Match a job against multiple resumes efficiently.
        
        Args:
            job_text: Job description text
            resume_texts: List of resume texts
            job_id: Optional job identifier
            
        Returns:
            List of MatchResults, sorted by score descending
        """
        results = []
        
        # Get job embedding once
        job_embedding = self.similarity_engine.get_embedding(job_text)
        
        # Extract job skills once
        job_skills_data = self.skills_extractor.extract_skills(job_text)
        job_skills = [s["skill"] for s in job_skills_data.get("skills", [])]
        
        for i, resume_text in enumerate(resume_texts):
            result = self.match(
                resume_text=resume_text,
                job_text=job_text,
                resume_id=f"resume_{i}",
                job_id=job_id
            )
            results.append(result)
        
        # Sort by overall score
        results.sort(key=lambda r: r.score.overall, reverse=True)
        
        return results
    
    def rank_candidates(
        self,
        job_text: str,
        resume_texts: List[str],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates for a job and return top matches.
        
        Returns list of dicts with rank, score, and match details.
        """
        results = self.match_batch(job_text, resume_texts)
        
        ranked = []
        for i, result in enumerate(results[:top_k]):
            ranked.append({
                "rank": i + 1,
                "resume_id": result.resume_id,
                "score": result.score.overall,
                "score_breakdown": result.score.to_dict(),
                "matched_skills": result.matched_skills,
                "missing_skills": result.missing_skills,
                "explanation": result.explanation
            })
        
        return ranked
    
    # ==================== SCORING METHODS ====================
    
    def _calculate_skills_score(
        self,
        resume_text: str,
        job_text: str,
        resume_data: Dict = None,
        job_data: Dict = None
    ) -> Tuple[float, Dict]:
        """Calculate skills matching score using semantic matching"""
        
        # Extract skills from both texts
        resume_skills_data = self.skills_extractor.extract_skills(resume_text)
        job_skills_data = self.skills_extractor.extract_skills(job_text)
        
        resume_skills = [s["skill"] for s in resume_skills_data.get("skills", [])]
        job_skills = [s["skill"] for s in job_skills_data.get("skills", [])]
        
        # If structured data provided, use those skills too
        if resume_data and "skills" in resume_data:
            if isinstance(resume_data["skills"], list):
                resume_skills.extend(resume_data["skills"])
        
        if job_data and "skills" in job_data:
            if isinstance(job_data["skills"], list):
                job_skills.extend(job_data["skills"])
        
        # Remove duplicates
        resume_skills = list(set(resume_skills))
        job_skills = list(set(job_skills))
        
        # No job skills found = rely on semantic score (already captured in main score)
        if not job_skills:
            # Use semantic similarity as proxy for skill relevance
            semantic_proxy = self.similarity_engine.calculate_similarity(resume_text, job_text)
            return semantic_proxy, {
                "matched_skills": resume_skills, 
                "missing_skills": [], 
                "match_score": semantic_proxy,
                "method": "semantic_proxy_no_job_skills"
            }
        
        # No resume skills found = use semantic matching on full text
        if not resume_skills:
            # Check if the resume text semantically matches job requirements
            semantic_proxy = self.similarity_engine.calculate_similarity(resume_text, job_text)
            # Low score since we couldn't identify specific skills
            score = semantic_proxy * 0.5  
            return score, {
                "matched_skills": [], 
                "missing_skills": job_skills, 
                "match_score": score,
                "method": "semantic_proxy_no_resume_skills"
            }
        
        # Semantic skill matching
        match_result = self.skills_extractor.match_skills(resume_skills, job_skills)
        
        return match_result["match_score"], {
            "matched_skills": match_result["matched_skills"],
            "missing_skills": match_result["missing_skills"],
            "match_details": match_result.get("match_details", {}),
            "resume_skills_count": len(resume_skills),
            "job_skills_count": len(job_skills)
        }
    
    def _calculate_experience_score(
        self,
        resume_text: str,
        job_text: str,
        resume_data: Dict = None,
        job_data: Dict = None
    ) -> float:
        """Calculate experience matching score"""
        
        # Extract years from job
        required_years = self._extract_years_required(job_text)
        
        # Extract years from resume
        resume_years = 0
        if resume_data and "years_experience" in resume_data:
            resume_years = resume_data["years_experience"]
        else:
            resume_years = self._estimate_years_from_text(resume_text)
        
        # No requirement = neutral score (not perfect)
        if required_years == 0:
            # If resume has experience, give partial credit
            if resume_years > 0:
                return min(0.7 + (resume_years * 0.05), 1.0)
            return 0.5  # Neutral when we can't determine
        
        # Calculate score
        if resume_years >= required_years:
            return 1.0
        elif resume_years > 0:
            return min(resume_years / required_years, 1.0)
        else:
            return 0.1  # Low score for unknown experience when required
    
    def _calculate_education_score(
        self,
        resume_text: str,
        job_text: str,
        resume_data: Dict = None,
        job_data: Dict = None
    ) -> float:
        """Calculate education matching score"""
        
        # Extract required education level
        required_level = self._extract_education_level(job_text)
        
        # Extract resume education level
        resume_level = 0
        if resume_data and "education_level" in resume_data:
            resume_level = self._get_education_value(resume_data["education_level"])
        else:
            resume_level = self._extract_education_level(resume_text)
        
        # No requirement = neutral score based on resume education
        if required_level == 0:
            if resume_level > 0:
                return min(0.5 + (resume_level * 0.1), 1.0)
            return 0.5  # Neutral when we can't determine
        
        # Calculate score
        if resume_level >= required_level:
            return 1.0
        elif resume_level > 0:
            return max(resume_level / required_level, 0.2)
        else:
            return 0.1  # Low score for unknown education when required
    
    def _calculate_confidence(
        self,
        resume_text: str,
        job_text: str,
        skill_details: Dict
    ) -> float:
        """Calculate confidence in the match score"""
        confidence = 0.5  # Base confidence
        
        # More text = more confidence
        if len(resume_text) > 500:
            confidence += 0.1
        if len(job_text) > 200:
            confidence += 0.1
        
        # More skills found = more confidence
        if skill_details.get("resume_skills_count", 0) > 5:
            confidence += 0.1
        if skill_details.get("job_skills_count", 0) > 3:
            confidence += 0.1
        
        # Skill matches increase confidence
        if len(skill_details.get("matched_skills", [])) > 3:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    # ==================== HELPER METHODS ====================
    
    def _extract_years_required(self, text: str) -> int:
        """Extract required years of experience from text"""
        patterns = [
            r'(\d+)\+?\s*(?:to\s+\d+\s*)?years?\s*(?:of\s*)?(?:experience|exp)',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*(?:minimum|required)'
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        return 0
    
    def _estimate_years_from_text(self, text: str) -> int:
        """Estimate years of experience from resume text"""
        # Look for explicit mentions
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\s*years?\s*in\s*(?:the\s*)?(?:industry|field)',
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        # Count date ranges to estimate
        year_pattern = r'20\d{2}|19\d{2}'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            years = [int(y) for y in years]
            return max(years) - min(years)
        
        return 0
    
    def _extract_education_level(self, text: str) -> float:
        """Extract education level from text"""
        text_lower = text.lower()
        
        # Check from highest to lowest
        for level, value in sorted(self.EDUCATION_LEVELS.items(), key=lambda x: -x[1]):
            if level in text_lower:
                return value
        return 0
    
    def _get_education_value(self, level: str) -> float:
        """Get numeric value for education level string"""
        if not level:
            return 0
        level_lower = level.lower()
        
        for key, value in self.EDUCATION_LEVELS.items():
            if key in level_lower:
                return value
        return 0
    
    def _generate_explanation(
        self,
        overall: float,
        semantic: float,
        skills: float,
        experience: float,
        education: float,
        skill_details: Dict
    ) -> str:
        """Generate human-readable explanation of the match"""
        
        # Overall assessment based on semantic similarity (the truth)
        if semantic >= 0.7:
            assessment = "Strong semantic match - resume content aligns well with job requirements"
        elif semantic >= 0.5:
            assessment = "Moderate semantic match - some relevant experience and skills"
        elif semantic >= 0.3:
            assessment = "Weak semantic match - limited alignment with job requirements"
        else:
            assessment = "Poor semantic match - resume appears unrelated to this position"
        
        parts = [f"{assessment}"]
        parts.append(f"Overall score: {overall:.0%} (Semantic: {semantic:.0%}, Skills: {skills:.0%})")
        
        # Skill analysis
        matched = skill_details.get("matched_skills", [])
        missing = skill_details.get("missing_skills", [])
        
        if matched:
            parts.append(f"Matched skills: {', '.join(matched[:5])}" + 
                        (f" (+{len(matched)-5} more)" if len(matched) > 5 else ""))
        
        if missing:
            parts.append(f"Missing/different skills: {', '.join(missing[:3])}" +
                        (f" (+{len(missing)-3} more)" if len(missing) > 3 else ""))
        
        # Score breakdown
        parts.append(f"Scores: Semantic {semantic:.0%}, Skills {skills:.0%}, " +
                    f"Experience {experience:.0%}, Education {education:.0%}")
        
        return " ".join(parts)


# Create singleton instance
matching_engine = MatchingEngine()
