from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class JobDescriptionBase(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Full job description text")


class JobDescriptionCreate(JobDescriptionBase):
    source: Optional[str] = Field("manual", description="Source of the job description")
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    scraped_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    requirements: Optional[str] = None
    source_url: Optional[str] = None
    status: Optional[str] = "active"


class JobDescriptionInDB(JobDescriptionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    source: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    scraped_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    requirements: Optional[str] = None
    source_url: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    extracted_skills: Optional[Dict[str, Any]] = None
    processing_errors: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime


class JobDescription(JobDescriptionInDB):
    """Full job description for API responses"""
    pass


class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    requirements: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    extracted_skills: Optional[Dict[str, Any]] = None
    processing_errors: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    

class JobDescriptionList(BaseModel):
    """Schema for paginated job description list"""
    items: List[JobDescription]
    total: int
    page: int
    size: int
    pages: int


class BulkJobDescriptionCreate(BaseModel):
    """Schema for bulk job description creation response"""
    successful: List[JobDescription]
    failed: List[Dict[str, Any]]
    total_created: int
    total_failed: int
