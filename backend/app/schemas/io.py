"""Pydantic I/O. Mirrors docs/BACKEND_API.md examples."""
from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str
    description: str


class JobOut(BaseModel):
    id: str
    title: str


class EvidenceItem(BaseModel):
    requirement_id: str
    quote: str
    sub: str = ""


class ScoreOut(BaseModel):
    overall: float
    subs: dict[str, float] = Field(default_factory=dict)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RankRow(BaseModel):
    candidate_id: str
    name: str
    overall: float
    tags: list[str] = Field(default_factory=list)


class CandidateDetail(BaseModel):
    candidate_id: str
    name: str
    filename: str = ""
    score: ScoreOut | None = None
