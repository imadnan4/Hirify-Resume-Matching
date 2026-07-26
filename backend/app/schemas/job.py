from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORMModel, PaginatedResponse


class JobDescriptionBase(ORMModel):
    id: int
    title: str
    company: str
    description: str
    source: str
    location: str | None = None
    salary_range: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    scraped_date: datetime | None = None
    processed_date: datetime | None = None
    requirements: str | None = None
    source_url: str | None = None
    structured_data: dict[str, Any] | None = None
    extracted_skills: list[str] | None = None
    processing_errors: dict[str, Any] | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class JobDescriptionCreate(BaseModel):
    title: str
    company: str
    description: str
    source: str = "manual"
    location: str | None = None
    salary_range: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    requirements: str | None = None
    source_url: str | None = None
    status: str = "active"


class JobDescriptionUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    description: str | None = None
    source: str | None = None
    location: str | None = None
    salary_range: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    requirements: str | None = None
    source_url: str | None = None
    structured_data: dict[str, Any] | None = None
    extracted_skills: list[str] | None = None
    processing_errors: dict[str, Any] | None = None
    status: str | None = None


class JobSkillsResponse(BaseModel):
    job_id: int
    title: str
    company: str
    extracted_skills: list[str] | None = None
    processed_date: datetime | None = None


class JobSearchMatch(BaseModel):
    id: int
    title: str
    company: str
    skill_matches: int
    matched_skills: list[str]


class JobSearchBySkillsResponse(BaseModel):
    jobs: list[JobSearchMatch]
    total_matches: int
    searched_skills: list[str]


JobListResponse = PaginatedResponse[JobDescriptionBase]
