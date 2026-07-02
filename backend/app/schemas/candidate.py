from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

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


class CandidateUpdate(BaseModel):
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


CandidateListResponse = PaginatedResponse[CandidateBase]
