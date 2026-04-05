"""Initial frontend-first backend schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_frontend_first_contract"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="manual"),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("salary_range", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=100), nullable=True),
        sa.Column("experience_level", sa.String(length=100), nullable=True),
        sa.Column("scraped_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("structured_data", sa.JSON(), nullable=True),
        sa.Column("extracted_skills", sa.JSON(), nullable=True),
        sa.Column("processing_errors", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("upload_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("structured_data", sa.JSON(), nullable=True),
        sa.Column("processing_errors", sa.JSON(), nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("linkedin_url", sa.String(length=1024), nullable=True),
        sa.Column("portfolio_url", sa.String(length=1024), nullable=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        sa.Column("education_level", sa.String(length=100), nullable=True),
        sa.Column("field_of_study", sa.String(length=255), nullable=True),
        sa.Column("university", sa.String(length=255), nullable=True),
        sa.Column("graduation_year", sa.Integer(), nullable=True),
        sa.Column("current_position", sa.String(length=255), nullable=True),
        sa.Column("current_company", sa.String(length=255), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("work_history", sa.JSON(), nullable=True),
        sa.Column("education_history", sa.JSON(), nullable=True),
        sa.Column("certifications", sa.JSON(), nullable=True),
        sa.Column("languages", sa.JSON(), nullable=True),
        sa.Column("projects", sa.JSON(), nullable=True),
        sa.Column("achievements", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("skills_score", sa.Float(), nullable=True),
        sa.Column("experience_score", sa.Float(), nullable=True),
        sa.Column("education_score", sa.Float(), nullable=True),
        sa.Column("additional_score", sa.Float(), nullable=True),
        sa.Column("matched_skills", sa.JSON(), nullable=True),
        sa.Column("missing_skills", sa.JSON(), nullable=True),
        sa.Column("skill_overlap_count", sa.Integer(), nullable=True),
        sa.Column("total_required_skills", sa.Integer(), nullable=True),
        sa.Column("explanation", sa.JSON(), nullable=True),
        sa.Column("confidence_level", sa.String(length=32), nullable=True),
        sa.Column("recommendation", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("resume_id", "job_id", name="uq_matches_resume_job"),
    )
    op.create_index("ix_matches_resume_id", "matches", ["resume_id"])
    op.create_index("ix_matches_job_id", "matches", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_matches_job_id", table_name="matches")
    op.drop_index("ix_matches_resume_id", table_name="matches")
    op.drop_table("matches")
    op.drop_table("candidates")
    op.drop_table("resumes")
    op.drop_table("jobs")
