from __future__ import annotations

from typing import Any

from sqlalchemy import Float, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Match(TimestampMixin, Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("resume_id", "job_id", name="uq_matches_resume_job"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    skills_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    additional_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    matched_skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    missing_skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    skill_overlap_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_required_skills: Mapped[int | None] = mapped_column(Integer, nullable=True)
    explanation: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    confidence_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(255), nullable=True)

    resume = relationship("Resume", back_populates="matches")
    job = relationship("JobDescription", back_populates="matches")
