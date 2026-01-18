"""Add embedding columns to resumes and jobs

Revision ID: 002_add_embeddings
Revises: 001
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_embeddings'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add embedding columns to resumes table
    op.add_column('resumes', 
        sa.Column('embedding', sa.LargeBinary(), nullable=True)
    )
    op.add_column('resumes', 
        sa.Column('embedding_model', sa.String(length=100), nullable=True)
    )
    
    # Add embedding columns to job_descriptions table
    op.add_column('job_descriptions', 
        sa.Column('embedding', sa.LargeBinary(), nullable=True)
    )
    op.add_column('job_descriptions', 
        sa.Column('embedding_model', sa.String(length=100), nullable=True)
    )
    
    # Add semantic_score to matches table
    op.add_column('matches', 
        sa.Column('semantic_score', sa.Float(), nullable=True)
    )
    
    # Add embedding column to skills table
    op.add_column('skills', 
        sa.Column('embedding', sa.LargeBinary(), nullable=True)
    )


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('skills', 'embedding')
    op.drop_column('matches', 'semantic_score')
    op.drop_column('job_descriptions', 'embedding_model')
    op.drop_column('job_descriptions', 'embedding')
    op.drop_column('resumes', 'embedding_model')
    op.drop_column('resumes', 'embedding')
