from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .resume import Resume
    from .job_description import JobDescription


class SingleMatchRequest(BaseModel):
    resume_id: int = Field(..., description="ID of the resume to match")
    job_id: int = Field(..., description="ID of the job description to match")


class MatchBase(BaseModel):
    resume_id: int = Field(..., description="ID of the resume")
    job_id: int = Field(..., description="ID of the job description")
    overall_score: float = Field(..., ge=0, le=1, description="Overall match score (0.0-1.0)")


class MatchCreate(MatchBase):
    skills_score: Optional[float] = Field(None, ge=0, le=1)
    experience_score: Optional[float] = Field(None, ge=0, le=1)
    education_score: Optional[float] = Field(None, ge=0, le=1)
    additional_score: Optional[float] = Field(None, ge=0, le=1)
    matched_skills: Optional[Dict[str, Any]] = None
    missing_skills: Optional[Dict[str, Any]] = None
    skill_overlap_count: Optional[int] = 0
    total_required_skills: Optional[int] = 0
    explanation: Optional[Dict[str, Any]] = None
    confidence_level: Optional[str] = None
    recommendation: Optional[str] = None


class MatchInDB(MatchBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    additional_score: Optional[float] = None
    matched_skills: Optional[Dict[str, Any]] = None
    missing_skills: Optional[Dict[str, Any]] = None
    skill_overlap_count: Optional[int] = 0
    total_required_skills: Optional[int] = 0
    explanation: Optional[Dict[str, Any]] = None
    confidence_level: Optional[str] = None
    recommendation: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Match(MatchInDB):
    """Full match information for API responses"""
    pass


class MatchWithDetails(Match):
    """Match with resume and job description details"""
    resume: Optional["Resume"] = None
    job_description: Optional["JobDescription"] = None


class MatchUpdate(BaseModel):
    overall_score: Optional[float] = Field(None, ge=0, le=1)
    skills_score: Optional[float] = Field(None, ge=0, le=1)
    experience_score: Optional[float] = Field(None, ge=0, le=1)
    education_score: Optional[float] = Field(None, ge=0, le=1)
    additional_score: Optional[float] = Field(None, ge=0, le=1)
    matched_skills: Optional[Dict[str, Any]] = None
    missing_skills: Optional[Dict[str, Any]] = None
    skill_overlap_count: Optional[int] = None
    total_required_skills: Optional[int] = None
    explanation: Optional[Dict[str, Any]] = None
    confidence_level: Optional[str] = None
    recommendation: Optional[str] = None


class MatchList(BaseModel):
    """Schema for paginated match list"""
    items: List[Match]
    total: int
    page: int
    size: int
    pages: int


class BulkMatchRequest(BaseModel):
    """Request schema for bulk matching"""
    resume_ids: List[int] = Field(..., description="List of resume IDs to match")
    job_ids: List[int] = Field(..., description="List of job description IDs to match")
    min_score_threshold: Optional[float] = Field(0.5, ge=0, le=1, description="Minimum score threshold (0.0-1.0)")
    include_explanations: bool = Field(True, description="Whether to include match explanations")


class BulkMatchResponse(BaseModel):
    """Response schema for bulk matching"""
    successful_matches: List[Match]
    failed_matches: List[Dict[str, Any]]
    total_matches: int
    processing_time: float
    summary: Dict[str, Any]


class MatchExplanation(BaseModel):
    """Detailed match explanation"""
    overall_score: float
    score_breakdown: Dict[str, float]
    matched_skills: List[str]
    missing_skills: List[str]
    skill_overlap_percentage: float
    experience_match: Dict[str, Any]
    education_match: Dict[str, Any]
    recommendations: List[str]


class MatchHistory(BaseModel):
    """Schema for match history tracking"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    match_id: int
    action: str
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class MatchHistoryCreate(BaseModel):
    match_id: int
    action: str
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class MatchStatistics(BaseModel):
    """Statistics about matches"""
    total_matches: int
    average_score: float
    score_distribution: Dict[str, int]
    top_matched_skills: List[Dict[str, Any]]
    match_trends: Dict[str, Any]
