from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel, PaginatedResponse


class CandidateBase(ORMModel):
    id: int
    resume_id: int
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    years_experience: int | None = None
    education_level: str | None = None
    field_of_study: str | None = None
    university: str | None = None
    graduation_year: int | None = None
    current_position: str | None = None
    current_company: str | None = None
    skills: list[str] | None = None
    work_history: list[dict[str, Any]] | None = None
    education_history: list[dict[str, Any]] | None = None
    certifications: list[str] | None = None
    summary: str | None = None
    created_at: datetime
    updated_at: datetime


_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CandidateUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=255)
    linkedin_url: str | None = Field(default=None, max_length=1024)
    portfolio_url: str | None = Field(default=None, max_length=1024)
    years_experience: int | None = Field(default=None, ge=0, le=60)
    education_level: str | None = Field(default=None, max_length=100)
    field_of_study: str | None = Field(default=None, max_length=255)
    university: str | None = Field(default=None, max_length=255)
    graduation_year: int | None = Field(default=None, ge=1900, le=2100)
    current_position: str | None = Field(default=None, max_length=255)
    current_company: str | None = Field(default=None, max_length=255)
    skills: list[str] | None = None
    work_history: list[dict[str, Any]] | None = None
    education_history: list[dict[str, Any]] | None = None
    certifications: list[str] | None = None
    summary: str | None = None

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        if value is not None and not _EMAIL_RE.match(value):
            raise ValueError(f"Invalid email format: {value}")
        return value

    @field_validator("linkedin_url", "portfolio_url")
    @classmethod
    def _validate_url(cls, value: str | None) -> str | None:
        if value is not None and not _URL_RE.match(value):
            raise ValueError(f"URL must start with http:// or https://: {value}")
        return value


class CandidateResumeResponse(BaseModel):
    candidate_id: int
    candidate_name: str | None
    resume_id: int
    resume_filename: str
    resume_status: str
    processed_date: datetime | None
    structured_data: dict[str, Any] | None


class CandidateSkillMatch(BaseModel):
    id: int
    resume_id: int
    full_name: str | None = None
    skill_matches: int
    matched_skills: list[str]


class CandidateSearchBySkillsResponse(BaseModel):
    candidates: list[CandidateSkillMatch]
    total_matches: int
    searched_skills: list[str]


class CandidateListBase(ORMModel):
    """Minimal candidate metadata for list responses — excludes PII."""
    id: int
    resume_id: int
    full_name: str | None = None
    location: str | None = None
    years_experience: int | None = None
    education_level: str | None = None
    current_position: str | None = None
    current_company: str | None = None
    skills: list[str] | None = None
    created_at: datetime
    updated_at: datetime


CandidateListResponse = PaginatedResponse[CandidateListBase]
