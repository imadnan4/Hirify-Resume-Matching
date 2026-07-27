from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel, PaginatedResponse

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_JOB_SOURCES = Literal["manual", "scraped", "imported"]
_JOB_STATUSES = Literal["active", "closed", "draft", "archived"]


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
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    source: _JOB_SOURCES = "manual"  # type: ignore[valid-type]
    location: str | None = Field(default=None, max_length=255)
    salary_range: str | None = Field(default=None, max_length=255)
    employment_type: str | None = Field(default=None, max_length=100)
    experience_level: str | None = Field(default=None, max_length=100)
    requirements: str | None = None
    source_url: str | None = Field(default=None, max_length=1024)
    status: _JOB_STATUSES = "active"  # type: ignore[valid-type]

    @field_validator("source_url")
    @classmethod
    def _validate_source_url(cls, value: str | None) -> str | None:
        if value is not None and not _URL_RE.match(value):
            raise ValueError(f"source_url must start with http:// or https://: {value}")
        return value


class JobDescriptionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    company: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    source: _JOB_SOURCES | None = None  # type: ignore[valid-type]
    location: str | None = Field(default=None, max_length=255)
    salary_range: str | None = Field(default=None, max_length=255)
    employment_type: str | None = Field(default=None, max_length=100)
    experience_level: str | None = Field(default=None, max_length=100)
    requirements: str | None = None
    source_url: str | None = Field(default=None, max_length=1024)
    structured_data: dict[str, Any] | None = None
    extracted_skills: list[str] | None = None
    processing_errors: dict[str, Any] | None = None
    status: _JOB_STATUSES | None = None  # type: ignore[valid-type]

    @field_validator("source_url")
    @classmethod
    def _validate_source_url(cls, value: str | None) -> str | None:
        if value is not None and not _URL_RE.match(value):
            raise ValueError(f"source_url must start with http:// or https://: {value}")
        return value


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
