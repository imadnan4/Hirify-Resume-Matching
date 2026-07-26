from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

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
    resume_id: int
    job_id: int


class BulkMatchRequest(BaseModel):
    resume_ids: list[int]
    job_ids: list[int]
    min_score_threshold: float = 0.5
    include_explanations: bool = True


class MatchUpdate(BaseModel):
    overall_score: float | None = None
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
