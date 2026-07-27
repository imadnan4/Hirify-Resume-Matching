from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel, PaginatedResponse


class MatchBase(ORMModel):
    id: int
    resume_id: int
    job_id: int
    overall_score: float
    skills_score: float | None = None
    experience_score: float | None = None
    education_score: float | None = None
    additional_score: float | None = None
    matched_skills: list[str] | None = None
    missing_skills: list[str] | None = None
    skill_overlap_count: int | None = None
    total_required_skills: int | None = None
    explanation: dict[str, Any] | None = None
    confidence_level: str | None = None
    recommendation: str | None = None
    created_at: datetime
    updated_at: datetime


class SingleMatchRequest(BaseModel):
    resume_id: int = Field(..., gt=0)
    job_id: int = Field(..., gt=0)


class BulkMatchRequest(BaseModel):
    resume_ids: list[int] = Field(..., min_length=1)
    job_ids: list[int] = Field(..., min_length=1)
    min_score_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    include_explanations: bool = True

    @model_validator(mode="after")
    def _validate_ids(self) -> "BulkMatchRequest":
        if any(rid <= 0 for rid in self.resume_ids):
            raise ValueError("resume_ids must all be positive integers")
        if any(jid <= 0 for jid in self.job_ids):
            raise ValueError("job_ids must all be positive integers")
        if len(set(self.resume_ids)) != len(self.resume_ids):
            raise ValueError("resume_ids contains duplicates")
        if len(set(self.job_ids)) != len(self.job_ids):
            raise ValueError("job_ids contains duplicates")
        return self


class MatchUpdate(BaseModel):
    overall_score: float | None = Field(default=None, ge=0.0, le=1.0)
    skills_score: float | None = Field(default=None, ge=0.0, le=1.0)
    experience_score: float | None = Field(default=None, ge=0.0, le=1.0)
    education_score: float | None = Field(default=None, ge=0.0, le=1.0)
    additional_score: float | None = Field(default=None, ge=0.0, le=1.0)
    matched_skills: list[str] | None = None
    missing_skills: list[str] | None = None
    skill_overlap_count: int | None = Field(default=None, ge=0)
    total_required_skills: int | None = Field(default=None, ge=0)
    explanation: dict[str, Any] | None = None
    confidence_level: str | None = None
    recommendation: str | None = None

    @model_validator(mode="after")
    def _validate_skill_counts(self) -> "MatchUpdate":
        if self.skill_overlap_count is not None and self.total_required_skills is not None:
            if self.skill_overlap_count > self.total_required_skills:
                raise ValueError("skill_overlap_count cannot exceed total_required_skills")
        return self


class MatchSummary(BaseModel):
    resume_id: int
    job_id: int
    overall_score: float
    matched_skills: list[str]
    missing_skills: list[str] | None = None
    explanation: dict[str, Any] | None = None


class BulkMatchResponse(BaseModel):
    total_matches: int
    matches: list[MatchSummary]
    processing_time_seconds: float


class MatchExplanationResponse(BaseModel):
    match_id: int
    explanation: dict[str, Any]


class MatchStatsResponse(BaseModel):
    total_matches: int
    average_score: float
    high_score_matches: int
    low_score_matches: int


class RankedCandidateResponse(BaseModel):
    rank: int
    resume_id: int
    candidate_name: str | None = None
    overall_score: float
    skills_score: float | None = None
    experience_score: float | None = None
    matched_skills: list[str]
    missing_skills: list[str]
    recommendation: str | None = None


MatchListResponse = PaginatedResponse[MatchBase]
