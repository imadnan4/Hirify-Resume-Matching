from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class CandidateBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class CandidateCreate(CandidateBase):
    resume_id: int = Field(..., description="ID of the associated resume")
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    work_history: Optional[Dict[str, Any]] = None
    education_history: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    languages: Optional[Dict[str, Any]] = None
    projects: Optional[Dict[str, Any]] = None
    achievements: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class CandidateInDB(CandidateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    resume_id: int
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    work_history: Optional[Dict[str, Any]] = None
    education_history: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    languages: Optional[Dict[str, Any]] = None
    projects: Optional[Dict[str, Any]] = None
    achievements: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Candidate(CandidateInDB):
    """Full candidate information for API responses"""
    pass


class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    work_history: Optional[Dict[str, Any]] = None
    education_history: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    languages: Optional[Dict[str, Any]] = None
    projects: Optional[Dict[str, Any]] = None
    achievements: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class CandidateList(BaseModel):
    """Schema for paginated candidate list"""
    items: List[Candidate]
    total: int
    page: int
    size: int
    pages: int


class CandidateScore(BaseModel):
    """Schema for candidate scoring"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    candidate_id: int
    score_type: str
    score_value: float
    calculation_method: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class CandidateScoreCreate(BaseModel):
    candidate_id: int
    score_type: str
    score_value: float
    calculation_method: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
