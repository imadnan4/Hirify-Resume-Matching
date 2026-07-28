from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.models.base import Base, TimestampMixin
from app.models.types import VectorOrJSON


class JobDescription(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary_range: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scraped_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    structured_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    extracted_skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    processing_errors: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorOrJSON(settings.embedding_dimensions), nullable=True
    )

    matches = relationship("Match", back_populates="job", cascade="all, delete-orphan")
