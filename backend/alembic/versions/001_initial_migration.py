"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-18 13:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create resumes table
    op.create_table('resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.Column('processed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=10), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('structured_data', sa.JSON(), nullable=True),
        sa.Column('processing_errors', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resumes_id'), 'resumes', ['id'], unique=False)
    
    # Create job_descriptions table
    op.create_table('job_descriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('scraped_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('structured_data', sa.JSON(), nullable=True),
        sa.Column('extracted_skills', sa.JSON(), nullable=True),
        sa.Column('processing_errors', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_descriptions_company'), 'job_descriptions', ['company'], unique=False)
    op.create_index(op.f('ix_job_descriptions_id'), 'job_descriptions', ['id'], unique=False)
    op.create_index(op.f('ix_job_descriptions_title'), 'job_descriptions', ['title'], unique=False)
    
    # Create skills table
    op.create_table('skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('aliases', sa.JSON(), nullable=True),
        sa.Column('confidence_threshold', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('popularity_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_skills_category'), 'skills', ['category'], unique=False)
    op.create_index(op.f('ix_skills_id'), 'skills', ['id'], unique=False)
    op.create_index(op.f('ix_skills_name'), 'skills', ['name'], unique=False)
    
    # Create candidates table
    op.create_table('candidates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('education_level', sa.String(length=100), nullable=True),
        sa.Column('field_of_study', sa.String(length=255), nullable=True),
        sa.Column('university', sa.String(length=255), nullable=True),
        sa.Column('graduation_year', sa.Integer(), nullable=True),
        sa.Column('current_position', sa.String(length=255), nullable=True),
        sa.Column('current_company', sa.String(length=255), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('work_history', sa.JSON(), nullable=True),
        sa.Column('education_history', sa.JSON(), nullable=True),
        sa.Column('certifications', sa.JSON(), nullable=True),
        sa.Column('languages', sa.JSON(), nullable=True),
        sa.Column('projects', sa.JSON(), nullable=True),
        sa.Column('achievements', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resume_id')
    )
    op.create_index(op.f('ix_candidates_email'), 'candidates', ['email'], unique=False)
    op.create_index(op.f('ix_candidates_full_name'), 'candidates', ['full_name'], unique=False)
    op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)
    
    # Create matches table
    op.create_table('matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('skills_score', sa.Float(), nullable=True),
        sa.Column('experience_score', sa.Float(), nullable=True),
        sa.Column('education_score', sa.Float(), nullable=True),
        sa.Column('additional_score', sa.Float(), nullable=True),
        sa.Column('matched_skills', sa.JSON(), nullable=True),
        sa.Column('missing_skills', sa.JSON(), nullable=True),
        sa.Column('skill_overlap_count', sa.Integer(), nullable=True),
        sa.Column('total_required_skills', sa.Integer(), nullable=True),
        sa.Column('explanation', sa.JSON(), nullable=True),
        sa.Column('confidence_level', sa.String(length=20), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job_descriptions.id'], ),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resume_id', 'job_id', name='unique_resume_job_match')
    )
    op.create_index(op.f('ix_matches_id'), 'matches', ['id'], unique=False)
    op.create_index(op.f('ix_matches_overall_score'), 'matches', ['overall_score'], unique=False)
    
    # Create skill_extractions table
    op.create_table('skill_extractions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('extraction_method', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_extractions_id'), 'skill_extractions', ['id'], unique=False)
    op.create_index(op.f('ix_skill_extractions_skill_name'), 'skill_extractions', ['skill_name'], unique=False)
    
    # Create candidate_scores table
    op.create_table('candidate_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('score_type', sa.String(length=50), nullable=False),
        sa.Column('score_value', sa.Float(), nullable=False),
        sa.Column('calculation_method', sa.String(length=100), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidate_scores_id'), 'candidate_scores', ['id'], unique=False)
    
    # Create match_history table
    op.create_table('match_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("datetime('now')"), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_match_history_id'), 'match_history', ['id'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('match_history')
    op.drop_table('candidate_scores')
    op.drop_table('skill_extractions')
    op.drop_table('matches')
    op.drop_table('candidates')
    op.drop_table('skills')
    op.drop_table('job_descriptions')
    op.drop_table('resumes')
