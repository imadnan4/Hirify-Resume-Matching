from celery import shared_task
from celery.utils.log import get_task_logger
from typing import Dict, Any, List
import asyncio
import traceback
from datetime import datetime

from app.services.matching_service import MatchingService
from app.core.database import SessionLocal
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match import Match
from app.models.candidate import Candidate

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def calculate_matches(self, resume_id: int, job_id: int) -> Dict[str, Any]:
    """
    Calculate match score between a single resume and job description
    """
    try:
        logger.info(f"Starting match calculation for resume {resume_id} and job {job_id}")
        
        self.update_state(state='PROGRESS', meta={'step': 'initializing', 'progress': 0})
        
        with SessionLocal() as db:
            # Get resume and job from database
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
            
            if not resume or not job:
                raise ValueError(f"Resume {resume_id} or Job {job_id} not found")
            
            # Check if match already exists
            existing_match = db.query(Match).filter(
                Match.resume_id == resume_id,
                Match.job_id == job_id
            ).first()
            
            if existing_match:
                logger.info(f"Match already exists for resume {resume_id} and job {job_id}")
                return {
                    'status': 'exists',
                    'match_id': existing_match.id,
                    'overall_score': existing_match.overall_score
                }
            
            # Initialize matching service
            matching_service = MatchingService()
            
            # Convert database objects to service objects
            self.update_state(state='PROGRESS', meta={'step': 'preparing_data', 'progress': 20})
            
            # Create ParsedResume object from database resume
            from app.services.resume_parser import ParsedResume, ContactInfo, WorkExperience, Education
            
            structured_data = resume.structured_data or {}
            contact_info = ContactInfo(**structured_data.get('contact_info', {}))
            
            work_experience = []
            for exp in structured_data.get('work_experience', []):
                work_experience.append(WorkExperience(**exp))
            
            education = []
            for edu in structured_data.get('education', []):
                education.append(Education(**edu))
            
            parsed_resume = ParsedResume(
                contact_info=contact_info,
                summary=structured_data.get('summary'),
                work_experience=work_experience,
                education=education,
                skills=structured_data.get('skills', {}),
                certifications=structured_data.get('certifications', []),
                languages=structured_data.get('languages', []),
                projects=structured_data.get('projects', []),
                achievements=structured_data.get('achievements', []),
                raw_text=resume.extracted_text,
                processing_metadata=structured_data.get('processing_metadata', {})
            )
            
            # Create JobDescription object
            from app.services.job_scraper import JobDescription as JobDescriptionService
            
            job_description = JobDescriptionService(
                title=job.title,
                company=job.company,
                description=job.description,
                requirements=job.requirements or "",
                location=job.location,
                salary_range=job.salary_range,
                employment_type=job.employment_type,
                source=job.source,
                source_url=job.source_url,
                skills=job.skills or [],
                experience_level=job.experience_level
            )
            
            # Calculate match score
            self.update_state(state='PROGRESS', meta={'step': 'calculating_match', 'progress': 50})
            
            # Run async matching in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                match_result = loop.run_until_complete(
                    matching_service.calculate_match_score(parsed_resume, job_description)
                )
            finally:
                loop.close()
            
            # Save match result to database
            self.update_state(state='PROGRESS', meta={'step': 'saving_match', 'progress': 80})
            
            db_match = Match(
                resume_id=resume_id,
                job_id=job_id,
                overall_score=match_result.match_score.overall_score,
                skills_score=match_result.match_score.skills_score,
                experience_score=match_result.match_score.experience_score,
                education_score=match_result.match_score.education_score,
                additional_score=match_result.match_score.additional_score,
                matched_skills=match_result.matched_skills,
                explanation={
                    'overall_explanation': match_result.match_score.explanation,
                    'skills_breakdown': match_result.experience_match,
                    'experience_breakdown': match_result.experience_match,
                    'education_breakdown': match_result.education_match,
                    'skill_gaps': match_result.skill_gaps,
                    'confidence': match_result.match_score.confidence
                }
            )
            
            db.add(db_match)
            db.commit()
            
            self.update_state(state='PROGRESS', meta={'step': 'completed', 'progress': 100})
            
            logger.info(f"Successfully calculated match for resume {resume_id} and job {job_id}")
            
            return {
                'status': 'success',
                'match_id': db_match.id,
                'resume_id': resume_id,
                'job_id': job_id,
                'overall_score': match_result.match_score.overall_score,
                'skills_score': match_result.match_score.skills_score,
                'experience_score': match_result.match_score.experience_score,
                'education_score': match_result.match_score.education_score,
                'matched_skills': match_result.matched_skills,
                'confidence': match_result.match_score.confidence
            }
            
    except Exception as exc:
        logger.error(f"Error calculating match for resume {resume_id} and job {job_id}: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying match calculation (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        
        return {
            'status': 'failed',
            'resume_id': resume_id,
            'job_id': job_id,
            'error': str(exc)
        }


@shared_task(bind=True)
def bulk_calculate_matches(self, resume_ids: List[int], job_ids: List[int]) -> Dict[str, Any]:
    """
    Calculate matches for multiple resume-job combinations
    """
    try:
        logger.info(f"Starting bulk match calculation for {len(resume_ids)} resumes and {len(job_ids)} jobs")
        
        results = []
        total_combinations = len(resume_ids) * len(job_ids)
        completed = 0
        
        for resume_id in resume_ids:
            for job_id in job_ids:
                self.update_state(
                    state='PROGRESS', 
                    meta={
                        'step': f'matching_resume_{resume_id}_job_{job_id}',
                        'progress': int((completed / total_combinations) * 100),
                        'current_resume': resume_id,
                        'current_job': job_id,
                        'completed': completed,
                        'total': total_combinations
                    }
                )
                
                # Calculate individual match
                result = calculate_matches.apply_async(args=[resume_id, job_id])
                results.append({
                    'resume_id': resume_id,
                    'job_id': job_id,
                    'task_id': result.id,
                    'status': 'queued'
                })
                
                completed += 1
        
        logger.info(f"Queued {len(results)} match calculation tasks")
        
        return {
            'status': 'success',
            'total_combinations': total_combinations,
            'queued_tasks': len(results),
            'task_results': results
        }
        
    except Exception as exc:
        logger.error(f"Error in bulk match calculation: {str(exc)}")
        return {
            'status': 'failed',
            'error': str(exc)
        }


@shared_task(bind=True)
def recalculate_matches_for_resume(self, resume_id: int) -> Dict[str, Any]:
    """
    Recalculate all matches for a specific resume (useful after resume reprocessing)
    """
    try:
        logger.info(f"Recalculating matches for resume {resume_id}")
        
        with SessionLocal() as db:
            # Get all active jobs
            active_jobs = db.query(JobDescription).filter(
                JobDescription.status == "active"
            ).all()
            
            job_ids = [job.id for job in active_jobs]
            
            # Delete existing matches for this resume
            db.query(Match).filter(Match.resume_id == resume_id).delete()
            db.commit()
            
            # Queue new match calculations
            results = []
            for job_id in job_ids:
                result = calculate_matches.apply_async(args=[resume_id, job_id])
                results.append({
                    'resume_id': resume_id,
                    'job_id': job_id,
                    'task_id': result.id,
                    'status': 'queued'
                })
            
            logger.info(f"Queued {len(results)} match recalculation tasks for resume {resume_id}")
            
            return {
                'status': 'success',
                'resume_id': resume_id,
                'recalculated_matches': len(results),
                'task_results': results
            }
            
    except Exception as exc:
        logger.error(f"Error recalculating matches for resume {resume_id}: {str(exc)}")
        return {
            'status': 'failed',
            'resume_id': resume_id,
            'error': str(exc)
        }


@shared_task(bind=True)
def recalculate_matches_for_job(self, job_id: int) -> Dict[str, Any]:
    """
    Recalculate all matches for a specific job (useful after job reprocessing)
    """
    try:
        logger.info(f"Recalculating matches for job {job_id}")
        
        with SessionLocal() as db:
            # Get all completed resumes
            completed_resumes = db.query(Resume).filter(
                Resume.status == "completed"
            ).all()
            
            resume_ids = [resume.id for resume in completed_resumes]
            
            # Delete existing matches for this job
            db.query(Match).filter(Match.job_id == job_id).delete()
            db.commit()
            
            # Queue new match calculations
            results = []
            for resume_id in resume_ids:
                result = calculate_matches.apply_async(args=[resume_id, job_id])
                results.append({
                    'resume_id': resume_id,
                    'job_id': job_id,
                    'task_id': result.id,
                    'status': 'queued'
                })
            
            logger.info(f"Queued {len(results)} match recalculation tasks for job {job_id}")
            
            return {
                'status': 'success',
                'job_id': job_id,
                'recalculated_matches': len(results),
                'task_results': results
            }
            
    except Exception as exc:
        logger.error(f"Error recalculating matches for job {job_id}: {str(exc)}")
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': str(exc)
        }
