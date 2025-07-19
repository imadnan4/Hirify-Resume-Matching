"""Database utility functions for initialization and seeding."""
import asyncio
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from .config import settings
from .database import Base, get_db
from ..models import *
import logging

logger = logging.getLogger(__name__)


def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Create database URL without database name for initial connection
        db_url_parts = settings.DATABASE_URL.split('/')
        db_name = db_url_parts[-1]
        base_url = '/'.join(db_url_parts[:-1])
        
        # Connect to PostgreSQL server
        engine = create_engine(f"{base_url}/postgres", isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
                
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise


def create_tables():
    """Create all tables in the database."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def seed_skills_data():
    """Seed the database with common skills."""
    skills_data = [
        # Programming Languages
        {"name": "Python", "category": "technical", "aliases": ["python", "py"], "popularity_score": 95.0},
        {"name": "JavaScript", "category": "technical", "aliases": ["js", "javascript", "es6"], "popularity_score": 90.0},
        {"name": "Java", "category": "technical", "aliases": ["java"], "popularity_score": 85.0},
        {"name": "C++", "category": "technical", "aliases": ["cpp", "c++"], "popularity_score": 70.0},
        {"name": "C#", "category": "technical", "aliases": ["csharp", "c#"], "popularity_score": 65.0},
        {"name": "PHP", "category": "technical", "aliases": ["php"], "popularity_score": 60.0},
        {"name": "Ruby", "category": "technical", "aliases": ["ruby"], "popularity_score": 55.0},
        {"name": "Go", "category": "technical", "aliases": ["golang", "go"], "popularity_score": 50.0},
        {"name": "Rust", "category": "technical", "aliases": ["rust"], "popularity_score": 45.0},
        {"name": "TypeScript", "category": "technical", "aliases": ["ts", "typescript"], "popularity_score": 80.0},
        
        # Web Technologies
        {"name": "React", "category": "technical", "aliases": ["react", "reactjs"], "popularity_score": 88.0},
        {"name": "Vue.js", "category": "technical", "aliases": ["vue", "vuejs"], "popularity_score": 75.0},
        {"name": "Angular", "category": "technical", "aliases": ["angular", "angularjs"], "popularity_score": 70.0},
        {"name": "Node.js", "category": "technical", "aliases": ["node", "nodejs"], "popularity_score": 85.0},
        {"name": "Express.js", "category": "technical", "aliases": ["express", "expressjs"], "popularity_score": 70.0},
        {"name": "HTML", "category": "technical", "aliases": ["html", "html5"], "popularity_score": 95.0},
        {"name": "CSS", "category": "technical", "aliases": ["css", "css3"], "popularity_score": 90.0},
        {"name": "SASS", "category": "technical", "aliases": ["sass", "scss"], "popularity_score": 60.0},
        {"name": "Bootstrap", "category": "technical", "aliases": ["bootstrap"], "popularity_score": 65.0},
        {"name": "Tailwind CSS", "category": "technical", "aliases": ["tailwind", "tailwindcss"], "popularity_score": 55.0},
        
        # Databases
        {"name": "PostgreSQL", "category": "technical", "aliases": ["postgres", "postgresql"], "popularity_score": 75.0},
        {"name": "MySQL", "category": "technical", "aliases": ["mysql"], "popularity_score": 80.0},
        {"name": "MongoDB", "category": "technical", "aliases": ["mongodb", "mongo"], "popularity_score": 70.0},
        {"name": "Redis", "category": "technical", "aliases": ["redis"], "popularity_score": 65.0},
        {"name": "SQLite", "category": "technical", "aliases": ["sqlite"], "popularity_score": 60.0},
        {"name": "Oracle", "category": "technical", "aliases": ["oracle"], "popularity_score": 55.0},
        {"name": "SQL Server", "category": "technical", "aliases": ["sqlserver", "mssql"], "popularity_score": 65.0},
        
        # Data Science & ML
        {"name": "Machine Learning", "category": "technical", "aliases": ["ml", "machine learning"], "popularity_score": 85.0},
        {"name": "Deep Learning", "category": "technical", "aliases": ["deep learning", "dl"], "popularity_score": 75.0},
        {"name": "TensorFlow", "category": "technical", "aliases": ["tensorflow"], "popularity_score": 70.0},
        {"name": "PyTorch", "category": "technical", "aliases": ["pytorch"], "popularity_score": 68.0},
        {"name": "scikit-learn", "category": "technical", "aliases": ["sklearn", "scikit-learn"], "popularity_score": 70.0},
        {"name": "Pandas", "category": "technical", "aliases": ["pandas"], "popularity_score": 75.0},
        {"name": "NumPy", "category": "technical", "aliases": ["numpy"], "popularity_score": 70.0},
        {"name": "Matplotlib", "category": "technical", "aliases": ["matplotlib"], "popularity_score": 65.0},
        {"name": "Seaborn", "category": "technical", "aliases": ["seaborn"], "popularity_score": 60.0},
        {"name": "Jupyter", "category": "technical", "aliases": ["jupyter"], "popularity_score": 65.0},
        
        # Cloud & DevOps
        {"name": "AWS", "category": "technical", "aliases": ["aws", "amazon web services"], "popularity_score": 85.0},
        {"name": "Azure", "category": "technical", "aliases": ["azure", "microsoft azure"], "popularity_score": 75.0},
        {"name": "Google Cloud", "category": "technical", "aliases": ["gcp", "google cloud"], "popularity_score": 70.0},
        {"name": "Docker", "category": "technical", "aliases": ["docker"], "popularity_score": 80.0},
        {"name": "Kubernetes", "category": "technical", "aliases": ["k8s", "kubernetes"], "popularity_score": 75.0},
        {"name": "Jenkins", "category": "technical", "aliases": ["jenkins"], "popularity_score": 65.0},
        {"name": "Git", "category": "technical", "aliases": ["git"], "popularity_score": 95.0},
        {"name": "GitHub", "category": "technical", "aliases": ["github"], "popularity_score": 90.0},
        {"name": "GitLab", "category": "technical", "aliases": ["gitlab"], "popularity_score": 70.0},
        {"name": "CI/CD", "category": "technical", "aliases": ["ci/cd", "continuous integration"], "popularity_score": 75.0},
        
        # Soft Skills
        {"name": "Communication", "category": "soft", "aliases": ["communication"], "popularity_score": 95.0},
        {"name": "Leadership", "category": "soft", "aliases": ["leadership"], "popularity_score": 85.0},
        {"name": "Team Work", "category": "soft", "aliases": ["teamwork", "collaboration"], "popularity_score": 90.0},
        {"name": "Problem Solving", "category": "soft", "aliases": ["problem solving"], "popularity_score": 90.0},
        {"name": "Critical Thinking", "category": "soft", "aliases": ["critical thinking"], "popularity_score": 85.0},
        {"name": "Project Management", "category": "soft", "aliases": ["project management"], "popularity_score": 80.0},
        {"name": "Time Management", "category": "soft", "aliases": ["time management"], "popularity_score": 85.0},
        {"name": "Analytical Skills", "category": "soft", "aliases": ["analytical skills"], "popularity_score": 80.0},
        {"name": "Creativity", "category": "soft", "aliases": ["creativity"], "popularity_score": 75.0},
        {"name": "Adaptability", "category": "soft", "aliases": ["adaptability"], "popularity_score": 80.0},
        
        # Certifications
        {"name": "AWS Certified", "category": "certification", "aliases": ["aws certified"], "popularity_score": 70.0},
        {"name": "PMP", "category": "certification", "aliases": ["pmp", "project management professional"], "popularity_score": 65.0},
        {"name": "Scrum Master", "category": "certification", "aliases": ["scrum master", "csm"], "popularity_score": 60.0},
        {"name": "Azure Certified", "category": "certification", "aliases": ["azure certified"], "popularity_score": 60.0},
        {"name": "Google Cloud Certified", "category": "certification", "aliases": ["gcp certified"], "popularity_score": 55.0},
    ]
    
    try:
        from .database import SessionLocal
        db = SessionLocal()
        
        for skill_data in skills_data:
            # Check if skill already exists
            existing_skill = db.query(Skill).filter(Skill.name == skill_data["name"]).first()
            if not existing_skill:
                skill = Skill(**skill_data)
                db.add(skill)
        
        db.commit()
        logger.info(f"Seeded {len(skills_data)} skills to database")
        
    except Exception as e:
        logger.error(f"Error seeding skills data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    """Initialize the database with tables and seed data."""
    logger.info("Initializing database...")
    
    # Create database if it doesn't exist
    create_database()
    
    # Create tables
    create_tables()
    
    # Seed initial data
    seed_skills_data()
    
    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    init_database()
