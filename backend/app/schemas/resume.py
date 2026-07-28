from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, PaginatedResponse


class ResumeListBase(ORMModel):
    """Minimal resume metadata for list responses — excludes sensitive fields."""
    id: int
    filename: str
    file_type: str
    file_size: int = Field(..., ge=0)
    upload_date: datetime
    processed_date: datetime | None = None
    status: Literal["pending", "processing", "completed", "failed"]
    created_at: datetime
    updated_at: datetime


class ResumeBase(ResumeListBase):
    """Full resume detail including extracted content — use only for authorized access."""
    extracted_text: str | None = None
    structured_data: dict[str, Any] | None = None
    processing_errors: dict[str, Any] | None = None


class ResumeUpdate(BaseModel):
    filename: str | None = None
    status: Literal["pending", "processing", "completed", "failed"] | None = None
    extracted_text: str | None = None
    structured_data: dict[str, Any] | None = None
    processing_errors: dict[str, Any] | None = None


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    status: str
    upload_date: datetime
    message: str = "Resume uploaded successfully"


class BulkResumeFailure(BaseModel):
    filename: str
    error: str


class BulkResumeUploadResponse(BaseModel):
    successful: list[ResumeUploadResponse]
    failed: list[BulkResumeFailure]
    total_uploaded: int
    total_failed: int


class ResumeStatusResponse(BaseModel):
    id: int
    filename: str
    status: str
    processed_date: datetime | None = None
    processing_errors: dict[str, Any] | None = None
    progress: int


class ContactInfoPreview(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None


class WorkExperiencePreview(BaseModel):
    job_title: str | None = None
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class EducationPreview(BaseModel):
    degree: str | None = None
    field_of_study: str | None = None
    institution: str | None = None
    graduation_year: int | None = None


class ResumePreviewResponse(BaseModel):
    contact_info: ContactInfoPreview = Field(default_factory=ContactInfoPreview)
    summary: str | None = None
    work_experience: list[WorkExperiencePreview] = Field(default_factory=list)
    education: list[EducationPreview] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    processing_metadata: dict[str, Any] = Field(default_factory=dict)


ResumeListResponse = PaginatedResponse[ResumeListBase]
