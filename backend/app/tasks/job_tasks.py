from celery import shared_task
from celery.utils.log import get_task_logger
from typing import Dict, Any, List
import asyncio
import traceback
from datetime import datetime

from app.services.job_scraper import JobScraper
from app.core.database import SessionLocal
from app.models.job_description import JobDescription
from app.schemas.job_description import JobDescriptionCreate

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def scrape_jobs(self, sources: List[str], search_terms: List[str], max_jobs: int = 100) -> Dict[str, Any]:
    """
    Scrape job descriptions from multiple sources
    """
    try:
        logger.info(f"Starting job scraping for sources: {sources}")
        
        # Update task progress
        self.update_state(state='PROGRESS', meta={'step': 'initializing', 'progress': 0})
        
        job_scraper = JobScraper()
        scraped_jobs = []
        total_sources = len(sources)
        
        for i, source in enumerate(sources):
            self.update_state(
                state='PROGRESS', 
                meta={
                    'step': f'scraping_{source}',
                    'progress': int((i / total_sources) * 80),
                    'current_source': source,
                    'completed': i,
                    'total': total_sources
                }
            )
            
            try:
                # Run async scraping in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    jobs = loop.run_until_complete(
                        job_scraper.scrape_jobs(source, search_terms, max_jobs // total_sources)
                    )
                    scraped_jobs.extend(jobs)
                finally:
                    loop.close()
                    
                logger.info(f"Scraped {len(jobs)} jobs from {source}")
                
            except Exception as source_exc:
                logger.error(f"Error scraping from {source}: {str(source_exc)}")
                continue
        
        # Save scraped jobs to database
        self.update_state(state='PROGRESS', meta={'step': 'saving_jobs', 'progress': 90})
        
        with SessionLocal() as db:
            saved_jobs = 0
            for job_data in scraped_jobs:
                try:
                    # Check for duplicates
                    existing_job = db.query(JobDescription).filter(
                        JobDescription.title == job_data.title,
                        JobDescription.company == job_data.company
                    ).first()
                    
                    if not existing_job:
                        # Create new job description
                        job_create = JobDescriptionCreate(
                            title=job_data.title,
                            company=job_data.company,
                            description=job_data.description,
                            requirements=job_data.requirements,
                            location=job_data.location,
                            salary_range=job_data.salary_range,
                            employment_type=job_data.employment_type,
                            source=job_data.source,
                            source_url=job_data.source_url,
                            skills=job_data.skills,
                            experience_level=job_data.experience_level
                        )
                        
                        db_job = JobDescription(**job_create.dict())
                        db_job.scraped_date = datetime.utcnow()
                        db_job.status = "active"
                        
                        db.add(db_job)
                        saved_jobs += 1
                        
                except Exception as job_exc:
                    logger.error(f"Error saving job: {str(job_exc)}")
                    continue
            
            db.commit()
        
        self.update_state(state='PROGRESS', meta={'step': 'completed', 'progress': 100})
        
        logger.info(f"Successfully scraped and saved {saved_jobs} jobs")
        
        return {
            'status': 'success',
            'total_scraped': len(scraped_jobs),
            'saved_jobs': saved_jobs,
            'sources': sources,
            'search_terms': search_terms
        }
        
    except Exception as exc:
        logger.error(f"Error in job scraping: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job scraping (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        
        return {
            'status': 'failed',
            'error': str(exc)
        }


@shared_task(bind=True, max_retries=3)
def process_scraped_job(self, job_id: int) -> Dict[str, Any]:
    """
    Process a scraped job description - extract skills, analyze requirements
    """
    try:
        logger.info(f"Starting job processing for ID: {job_id}")
        
        self.update_state(state='PROGRESS', meta={'step': 'initializing', 'progress': 0})
        
        with SessionLocal() as db:
            job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
            if not job:
                raise ValueError(f"Job with ID {job_id} not found")
            
            # Update status
            job.status = "processing"
            job.processed_date = datetime.utcnow()
            db.commit()
            
            # Initialize job scraper for processing
            job_scraper = JobScraper()
            
            # Step 1: Extract skills from job description
            self.update_state(state='PROGRESS', meta={'step': 'extracting_skills', 'progress': 30})
            
            # Run async processing in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                job_analysis = loop.run_until_complete(
                    job_scraper.analyze_job_description(
                        job.description + " " + (job.requirements or "")
                    )
                )
            finally:
                loop.close()
            
            # Step 2: Update job with extracted information
            self.update_state(state='PROGRESS', meta={'step': 'updating_job', 'progress': 70})
            
            # Update job with analysis results
            if hasattr(job_analysis, 'skills'):
                job.skills = job_analysis.skills
            if hasattr(job_analysis, 'experience_level'):
                job.experience_level = job_analysis.experience_level
            if hasattr(job_analysis, 'education_requirements'):
                job.education_requirements = job_analysis.education_requirements
            
            # Update structured data
            job.structured_data = {
                'extracted_skills': job_analysis.skills if hasattr(job_analysis, 'skills') else [],
                'experience_level': job_analysis.experience_level if hasattr(job_analysis, 'experience_level') else None,
                'education_requirements': job_analysis.education_requirements if hasattr(job_analysis, 'education_requirements') else [],
                'salary_mentioned': job_analysis.salary_range if hasattr(job_analysis, 'salary_range') else None,
                'remote_friendly': job_analysis.remote_friendly if hasattr(job_analysis, 'remote_friendly') else False,
                'processing_metadata': {
                    'processed_at': datetime.utcnow().isoformat(),
                    'text_length': len(job.description + " " + (job.requirements or "")),
                    'skills_found': len(job_analysis.skills) if hasattr(job_analysis, 'skills') else 0
                }
            }
            
            job.status = "completed"
            db.commit()
            
            self.update_state(state='PROGRESS', meta={'step': 'completed', 'progress': 100})
            
            logger.info(f"Successfully processed job ID: {job_id}")
            
            return {
                'status': 'success',
                'job_id': job_id,
                'skills_found': len(job_analysis.skills) if hasattr(job_analysis, 'skills') else 0,
                'experience_level': job_analysis.experience_level if hasattr(job_analysis, 'experience_level') else None,
                'processing_time': (datetime.utcnow() - job.processed_date).total_seconds()
            }
            
    except Exception as exc:
        logger.error(f"Error processing job {job_id}: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Update job status to failed
        try:
            with SessionLocal() as db:
                job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
                if job:
                    job.status = "failed"
                    db.commit()
        except Exception:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job processing for ID: {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': str(exc)
        }
