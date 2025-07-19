import asyncio
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import re
import math
from collections import Counter

from .similarity_engine import SimilarityEngine
from .skills_extractor import SkillsExtractor
from .resume_parser import ParsedResume
from .job_scraper import JobDescription


@dataclass
class MatchScore:
    """Detailed match score breakdown"""
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    additional_score: float
    confidence: float
    explanation: str


@dataclass
class MatchResult:
    """Complete match result with detailed information"""
    resume_id: str
    job_id: str
    match_score: MatchScore
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    skill_gaps: List[str] = field(default_factory=list)
    experience_match: Dict[str, Any] = field(default_factory=dict)
    education_match: Dict[str, Any] = field(default_factory=dict)
    salary_match: Optional[Dict[str, Any]] = None
    location_match: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match result to dictionary"""
        return {
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'overall_score': self.match_score.overall_score,
            'skills_score': self.match_score.skills_score,
            'experience_score': self.match_score.experience_score,
            'education_score': self.match_score.education_score,
            'additional_score': self.match_score.additional_score,
            'confidence': self.match_score.confidence,
            'explanation': self.match_score.explanation,
            'matched_skills': self.matched_skills,
            'missing_skills': self.missing_skills,
            'skill_gaps': self.skill_gaps,
            'experience_match': self.experience_match,
            'education_match': self.education_match,
            'salary_match': self.salary_match,
            'location_match': self.location_match,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class RankedCandidate:
    """Ranked candidate with match information"""
    resume_id: str
    candidate_name: str
    match_result: MatchResult
    rank: int
    percentile: float


class MatchingService:
    """Intelligent resume-job matching service with advanced scoring"""
    
    def __init__(self):
        self.similarity_engine = SimilarityEngine()
        self.skills_extractor = SkillsExtractor()
        
        # Scoring weights (should sum to 1.0)
        self.scoring_weights = {
            'skills': 0.40,        # 40% - Technical and soft skills match
            'experience': 0.30,    # 30% - Years and domain experience
            'education': 0.20,     # 20% - Degree level and field alignment
            'additional': 0.10     # 10% - Certifications, keywords, location
        }
        
        # Experience level mappings
        self.experience_levels = {
            'entry': (0, 2),
            'junior': (1, 3),
            'mid': (3, 6),
            'senior': (5, 10),
            'lead': (7, 15),
            'principal': (10, 20),
            'staff': (12, 25)
        }
        
        # Education level hierarchy
        self.education_hierarchy = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'mba': 4.5,
            'phd': 5,
            'doctorate': 5
        }
    
    def calculate_skills_score(self, resume: ParsedResume, job: JobDescription) -> Tuple[float, Dict[str, Any]]:
        """Calculate skills matching score (40% weight)"""
        try:
            # Extract skills from resume and job
            resume_skills = set()
            if resume.skills and 'skills' in resume.skills:
                resume_skills = set(skill['skill'].lower() for skill in resume.skills['skills'])
            
            job_skills = set(skill.lower() for skill in job.skills) if job.skills else set()
            
            # If no skills found, use text similarity
            if not resume_skills and not job_skills:
                resume_text = f"{resume.summary or ''} {' '.join([exp.description or '' for exp in resume.work_experience])}"
                job_text = f"{job.description} {job.requirements}"
                text_similarity = self.similarity_engine.calculate_semantic_similarity(resume_text, job_text)
                return text_similarity, {
                    'method': 'text_similarity',
                    'matched_skills': [],
                    'missing_skills': [],
                    'skill_overlap': 0.0
                }
            
            # Calculate skill overlap
            matched_skills = list(resume_skills.intersection(job_skills))
            missing_skills = list(job_skills - resume_skills)
            
            if len(job_skills) == 0:
                skill_overlap = 1.0 if len(resume_skills) > 0 else 0.5
            else:
                skill_overlap = len(matched_skills) / len(job_skills)
            
            # Fuzzy matching for similar skills
            fuzzy_matches = []
            for job_skill in missing_skills:
                fuzzy_candidates = self.skills_extractor.fuzzy_match_skills(job_skill, threshold=0.7)
                for candidate in fuzzy_candidates:
                    if candidate.lower() in resume_skills:
                        fuzzy_matches.append((job_skill, candidate))
                        break
            
            # Adjust score based on fuzzy matches
            fuzzy_score_boost = len(fuzzy_matches) * 0.5 / len(job_skills) if job_skills else 0
            
            # Calculate priority skills bonus
            priority_skills = ['python', 'machine learning', 'java', 'react', 'aws', 'docker', 'kubernetes']
            priority_matches = len([skill for skill in matched_skills if skill in priority_skills])
            priority_bonus = min(priority_matches * 0.1, 0.3)  # Max 30% bonus
            
            # Final skills score
            skills_score = min(skill_overlap + fuzzy_score_boost + priority_bonus, 1.0)
            
            return skills_score, {
                'method': 'skills_matching',
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'fuzzy_matches': fuzzy_matches,
                'skill_overlap': skill_overlap,
                'priority_bonus': priority_bonus,
                'total_resume_skills': len(resume_skills),
                'total_job_skills': len(job_skills)
            }
            
        except Exception as e:
            print(f"Error calculating skills score: {e}")
            return 0.0, {'error': str(e)}
    
    def calculate_experience_score(self, resume: ParsedResume, job: JobDescription) -> Tuple[float, Dict[str, Any]]:
        """Calculate experience matching score (30% weight)"""
        try:
            # Extract years of experience
            resume_years = resume.processing_metadata.get('total_years_experience', 0)
            
            # Extract required experience from job
            job_years_required = self._extract_required_experience(job.description + " " + job.requirements)
            
            # Calculate experience match
            if job_years_required == 0:
                years_match = 1.0  # No specific requirement
            elif resume_years >= job_years_required:
                # Give full score if meets requirement, bonus for overqualification (up to 10%)
                overqualification_bonus = min((resume_years - job_years_required) * 0.02, 0.1)
                years_match = min(1.0 + overqualification_bonus, 1.0)
            else:
                # Partial score if underqualified
                years_match = max(resume_years / job_years_required, 0.2)
            
            # Calculate domain experience match
            domain_match = self._calculate_domain_experience_match(resume, job)
            
            # Combine years and domain experience
            experience_score = (years_match * 0.6) + (domain_match * 0.4)
            
            return experience_score, {
                'resume_years': resume_years,
                'job_years_required': job_years_required,
                'years_match': years_match,
                'domain_match': domain_match,
                'combined_score': experience_score
            }
            
        except Exception as e:
            print(f"Error calculating experience score: {e}")
            return 0.0, {'error': str(e)}
    
    def calculate_education_score(self, resume: ParsedResume, job: JobDescription) -> Tuple[float, Dict[str, Any]]:
        """Calculate education matching score (20% weight)"""
        try:
            # Extract education from resume
            resume_education_level = 0
            resume_field = ""
            
            if resume.education:
                for edu in resume.education:
                    if edu.degree:
                        level = self._extract_education_level(edu.degree)
                        if level > resume_education_level:
                            resume_education_level = level
                            resume_field = edu.field_of_study or ""
            
            # Extract required education from job
            job_education_required = self._extract_required_education(job.description + " " + job.requirements)
            job_field_preferred = self._extract_preferred_field(job.description + " " + job.requirements)
            
            # Calculate education level match
            if job_education_required == 0:
                level_match = 1.0  # No specific requirement
            elif resume_education_level >= job_education_required:
                level_match = 1.0
            else:
                level_match = max(resume_education_level / job_education_required, 0.3)
            
            # Calculate field match
            field_match = self._calculate_field_match(resume_field, job_field_preferred)
            
            # Combine level and field match
            education_score = (level_match * 0.7) + (field_match * 0.3)
            
            return education_score, {
                'resume_education_level': resume_education_level,
                'job_education_required': job_education_required,
                'resume_field': resume_field,
                'job_field_preferred': job_field_preferred,
                'level_match': level_match,
                'field_match': field_match,
                'combined_score': education_score
            }
            
        except Exception as e:
            print(f"Error calculating education score: {e}")
            return 0.0, {'error': str(e)}
    
    def calculate_additional_score(self, resume: ParsedResume, job: JobDescription) -> Tuple[float, Dict[str, Any]]:
        """Calculate additional factors score (10% weight)"""
        try:
            factors = {}
            total_score = 0.0
            
            # Certifications match
            cert_score = self._calculate_certifications_match(resume.certifications or [], job.skills or [])
            factors['certifications'] = cert_score
            total_score += cert_score * 0.4
            
            # Keywords match (beyond skills)
            keyword_score = self._calculate_keyword_match(resume, job)
            factors['keywords'] = keyword_score
            total_score += keyword_score * 0.3
            
            # Location match
            location_score = self._calculate_location_match(resume, job)
            factors['location'] = location_score
            total_score += location_score * 0.2
            
            # Company size/type preference
            company_score = self._calculate_company_match(resume, job)
            factors['company'] = company_score
            total_score += company_score * 0.1
            
            return total_score, factors
            
        except Exception as e:
            print(f"Error calculating additional score: {e}")
            return 0.0, {'error': str(e)}
    
    def _extract_required_experience(self, text: str) -> int:
        """Extract required years of experience from job text"""
        patterns = [
            r'(\d+)\+?\s*(?:to\s+\d+\s*)?years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*(?:to\s+\d+\s*)?yrs?\s*(?:of\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*minimum'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    def _calculate_domain_experience_match(self, resume: ParsedResume, job: JobDescription) -> float:
        """Calculate domain-specific experience match"""
        try:
            # Extract domain from job
            job_domain = self._extract_job_domain(job.title + " " + job.description)
            
            # Check resume work experience for domain match
            domain_experience = 0
            for exp in resume.work_experience:
                if exp.title and exp.description:
                    exp_text = exp.title + " " + exp.description
                    if self._check_domain_match(exp_text, job_domain):
                        domain_experience += 1
            
            if len(resume.work_experience) == 0:
                return 0.5  # Neutral score if no experience data
            
            return min(domain_experience / len(resume.work_experience), 1.0)
            
        except Exception:
            return 0.5
    
    def _extract_job_domain(self, text: str) -> str:
        """Extract job domain from text"""
        domains = {
            'software': ['software', 'programming', 'development', 'coding'],
            'data': ['data', 'analytics', 'machine learning', 'ai', 'statistics'],
            'frontend': ['frontend', 'ui', 'ux', 'react', 'angular', 'vue'],
            'backend': ['backend', 'api', 'server', 'database', 'microservices'],
            'devops': ['devops', 'infrastructure', 'deployment', 'aws', 'docker'],
            'mobile': ['mobile', 'android', 'ios', 'react native', 'flutter'],
            'security': ['security', 'cybersecurity', 'penetration', 'vulnerability'],
            'finance': ['finance', 'fintech', 'banking', 'trading', 'payments'],
            'healthcare': ['healthcare', 'medical', 'health', 'clinical', 'pharma']
        }
        
        text_lower = text.lower()
        for domain, keywords in domains.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
        
        return 'general'
    
    def _check_domain_match(self, experience_text: str, job_domain: str) -> bool:
        """Check if experience matches job domain"""
        exp_domain = self._extract_job_domain(experience_text)
        return exp_domain == job_domain or exp_domain in ['software', 'general']
    
    def _extract_education_level(self, degree: str) -> int:
        """Extract education level from degree string"""
        degree_lower = degree.lower()
        
        for level, value in self.education_hierarchy.items():
            if level in degree_lower:
                return value
        
        return 0
    
    def _extract_required_education(self, text: str) -> int:
        """Extract required education level from job text"""
        text_lower = text.lower()
        
        requirements = [
            ('phd', 5), ('doctorate', 5), ('doctoral', 5),
            ('mba', 4.5), ('master', 4), ('masters', 4),
            ('bachelor', 3), ('bachelors', 3), ('bs', 3), ('ba', 3),
            ('associate', 2), ('associates', 2),
            ('high school', 1), ('diploma', 1)
        ]
        
        for requirement, level in requirements:
            if requirement in text_lower:
                return level
        
        return 0
    
    def _extract_preferred_field(self, text: str) -> str:
        """Extract preferred field of study from job text"""
        fields = {
            'computer science': ['computer science', 'cs', 'computer engineering'],
            'engineering': ['engineering', 'mechanical', 'electrical', 'civil'],
            'mathematics': ['mathematics', 'math', 'statistics', 'statistical'],
            'business': ['business', 'management', 'administration', 'mba'],
            'data science': ['data science', 'analytics', 'data analytics'],
            'information technology': ['information technology', 'it', 'mis'],
            'finance': ['finance', 'accounting', 'economics', 'financial']
        }
        
        text_lower = text.lower()
        for field, keywords in fields.items():
            if any(keyword in text_lower for keyword in keywords):
                return field
        
        return 'general'
    
    def _calculate_field_match(self, resume_field: str, job_field: str) -> float:
        """Calculate field of study match"""
        if not resume_field or not job_field or job_field == 'general':
            return 0.5  # Neutral score
        
        if resume_field.lower() == job_field.lower():
            return 1.0
        
        # Check for related fields
        related_fields = {
            'computer science': ['engineering', 'information technology', 'data science'],
            'engineering': ['computer science', 'mathematics'],
            'data science': ['computer science', 'mathematics', 'statistics'],
            'mathematics': ['data science', 'engineering', 'computer science'],
            'business': ['finance', 'economics']
        }
        
        resume_field_lower = resume_field.lower()
        job_field_lower = job_field.lower()
        
        if job_field_lower in related_fields.get(resume_field_lower, []):
            return 0.7
        
        return 0.2
    
    def _calculate_certifications_match(self, resume_certs: List[str], job_skills: List[str]) -> float:
        """Calculate certifications match score"""
        if not resume_certs or not job_skills:
            return 0.5
        
        cert_skills = set(cert.lower() for cert in resume_certs)
        job_skills_set = set(skill.lower() for skill in job_skills)
        
        matches = len(cert_skills.intersection(job_skills_set))
        return min(matches / len(job_skills_set), 1.0) if job_skills_set else 0.5
    
    def _calculate_keyword_match(self, resume: ParsedResume, job: JobDescription) -> float:
        """Calculate keyword match beyond skills"""
        resume_text = f"{resume.summary or ''} {' '.join([exp.description or '' for exp in resume.work_experience])}"
        job_text = f"{job.description} {job.requirements}"
        
        return self.similarity_engine.calculate_semantic_similarity(resume_text, job_text)
    
    def _calculate_location_match(self, resume: ParsedResume, job: JobDescription) -> float:
        """Calculate location match score"""
        # Simple implementation - can be enhanced with geolocation
        if not job.location:
            return 1.0  # Remote or no location requirement
        
        if 'remote' in job.location.lower():
            return 1.0
        
        # Default neutral score - would need actual location data to improve
        return 0.5
    
    def _calculate_company_match(self, resume: ParsedResume, job: JobDescription) -> float:
        """Calculate company type/size match"""
        # Simple implementation - can be enhanced with company data
        return 0.5
    
    def calculate_match_score(self, resume: ParsedResume, job: JobDescription) -> MatchResult:
        """Calculate comprehensive match score between resume and job"""
        try:
            # Calculate individual scores
            skills_score, skills_details = self.calculate_skills_score(resume, job)
            experience_score, experience_details = self.calculate_experience_score(resume, job)
            education_score, education_details = self.calculate_education_score(resume, job)
            additional_score, additional_details = self.calculate_additional_score(resume, job)
            
            # Calculate weighted overall score
            overall_score = (
                skills_score * self.scoring_weights['skills'] +
                experience_score * self.scoring_weights['experience'] +
                education_score * self.scoring_weights['education'] +
                additional_score * self.scoring_weights['additional']
            )
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(resume, job, skills_details, experience_details, education_details)
            
            # Generate explanation
            explanation = self._generate_explanation(
                overall_score, skills_score, experience_score, 
                education_score, additional_score, skills_details
            )
            
            # Create match score object
            match_score = MatchScore(
                overall_score=round(overall_score, 3),
                skills_score=round(skills_score, 3),
                experience_score=round(experience_score, 3),
                education_score=round(education_score, 3),
                additional_score=round(additional_score, 3),
                confidence=round(confidence, 3),
                explanation=explanation
            )
            
            # Create match result
            match_result = MatchResult(
                resume_id=str(hash(resume.raw_text[:100])),  # Simple ID generation
                job_id=job.job_id or str(hash(job.title + job.company)),
                match_score=match_score,
                matched_skills=skills_details.get('matched_skills', []),
                missing_skills=skills_details.get('missing_skills', []),
                experience_match=experience_details,
                education_match=education_details
            )
            
            return match_result
            
        except Exception as e:
            print(f"Error calculating match score: {e}")
            # Return minimal result on error
            return MatchResult(
                resume_id=str(hash(resume.raw_text[:100])),
                job_id=job.job_id or str(hash(job.title + job.company)),
                match_score=MatchScore(
                    overall_score=0.0,
                    skills_score=0.0,
                    experience_score=0.0,
                    education_score=0.0,
                    additional_score=0.0,
                    confidence=0.0,
                    explanation=f"Error calculating match: {str(e)}"
                )
            )
    
    def _calculate_confidence(self, resume: ParsedResume, job: JobDescription, 
                           skills_details: Dict, experience_details: Dict, 
                           education_details: Dict) -> float:
        """Calculate confidence score based on data completeness"""
        confidence_factors = []
        
        # Resume data completeness
        if resume.contact_info.full_name:
            confidence_factors.append(0.1)
        if resume.work_experience:
            confidence_factors.append(0.2)
        if resume.education:
            confidence_factors.append(0.15)
        if resume.skills and resume.skills.get('skills'):
            confidence_factors.append(0.2)
        
        # Job data completeness
        if job.description:
            confidence_factors.append(0.15)
        if job.requirements:
            confidence_factors.append(0.1)
        if job.skills:
            confidence_factors.append(0.1)
        
        return sum(confidence_factors)
    
    def _generate_explanation(self, overall_score: float, skills_score: float, 
                            experience_score: float, education_score: float,
                            additional_score: float, skills_details: Dict) -> str:
        """Generate human-readable explanation of match score"""
        explanations = []
        
        # Overall assessment
        if overall_score >= 0.8:
            explanations.append("Excellent match with strong alignment across all criteria.")
        elif overall_score >= 0.6:
            explanations.append("Good match with solid alignment in most areas.")
        elif overall_score >= 0.4:
            explanations.append("Moderate match with some alignment but gaps in key areas.")
        else:
            explanations.append("Limited match with significant gaps in requirements.")
        
        # Skills assessment
        if skills_score >= 0.8:
            explanations.append("Strong skills match with most required skills present.")
        elif skills_score >= 0.6:
            explanations.append("Good skills match with key skills covered.")
        elif skills_score >= 0.4:
            explanations.append("Moderate skills match with some missing requirements.")
        else:
            explanations.append("Limited skills match with significant skill gaps.")
        
        # Experience assessment
        if experience_score >= 0.8:
            explanations.append("Experience level well-matched for the position.")
        elif experience_score >= 0.6:
            explanations.append("Experience level mostly appropriate.")
        elif experience_score >= 0.4:
            explanations.append("Experience level somewhat below requirements.")
        else:
            explanations.append("Experience level significantly below requirements.")
        
        # Add specific skill information
        matched_skills = skills_details.get('matched_skills', [])
        missing_skills = skills_details.get('missing_skills', [])
        
        if matched_skills:
            explanations.append(f"Matched skills: {', '.join(matched_skills[:5])}")
        if missing_skills:
            explanations.append(f"Missing skills: {', '.join(missing_skills[:5])}")
        
        return " ".join(explanations)
    
    async def bulk_match(self, resumes: List[ParsedResume], jobs: List[JobDescription],
                        min_score_threshold: float = 0.0) -> List[MatchResult]:
        """Perform bulk matching of resumes against jobs"""
        results = []
        
        for resume in resumes:
            for job in jobs:
                match_result = self.calculate_match_score(resume, job)
                
                if match_result.match_score.overall_score >= min_score_threshold:
                    results.append(match_result)
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x.match_score.overall_score, reverse=True)
        
        return results
    
    def rank_candidates(self, matches: List[MatchResult], job_id: str) -> List[RankedCandidate]:
        """Rank candidates for a specific job"""
        # Filter matches for the specific job
        job_matches = [match for match in matches if match.job_id == job_id]
        
        if not job_matches:
            return []
        
        # Sort by overall score
        job_matches.sort(key=lambda x: x.match_score.overall_score, reverse=True)
        
        # Create ranked candidates
        ranked_candidates = []
        total_candidates = len(job_matches)
        
        for i, match in enumerate(job_matches):
            rank = i + 1
            percentile = ((total_candidates - i) / total_candidates) * 100
            
            ranked_candidate = RankedCandidate(
                resume_id=match.resume_id,
                candidate_name=f"Candidate {match.resume_id[:8]}",  # Placeholder
                match_result=match,
                rank=rank,
                percentile=round(percentile, 1)
            )
            
            ranked_candidates.append(ranked_candidate)
        
        return ranked_candidates
    
    def explain_match(self, match_result: MatchResult) -> Dict[str, Any]:
        """Provide detailed explanation of a match result"""
        return {
            'overall_assessment': match_result.match_score.explanation,
            'score_breakdown': {
                'overall': match_result.match_score.overall_score,
                'skills': match_result.match_score.skills_score,
                'experience': match_result.match_score.experience_score,
                'education': match_result.match_score.education_score,
                'additional': match_result.match_score.additional_score
            },
            'skills_analysis': {
                'matched_skills': match_result.matched_skills,
                'missing_skills': match_result.missing_skills,
                'skill_gaps': match_result.skill_gaps
            },
            'experience_analysis': match_result.experience_match,
            'education_analysis': match_result.education_match,
            'confidence': match_result.match_score.confidence,
            'recommendations': self._generate_recommendations(match_result)
        }
    
    def _generate_recommendations(self, match_result: MatchResult) -> List[str]:
        """Generate recommendations for improving match score"""
        recommendations = []
        
        # Skills recommendations
        if match_result.match_score.skills_score < 0.7:
            if match_result.missing_skills:
                recommendations.append(f"Consider developing skills in: {', '.join(match_result.missing_skills[:3])}")
        
        # Experience recommendations
        if match_result.match_score.experience_score < 0.7:
            recommendations.append("Consider gaining more relevant experience in the field")
        
        # Education recommendations
        if match_result.match_score.education_score < 0.7:
            recommendations.append("Consider pursuing additional education or certifications")
        
        return recommendations
