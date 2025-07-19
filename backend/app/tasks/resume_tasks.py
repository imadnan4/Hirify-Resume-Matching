from celery import shared_task
from celery.utils.log import get_task_logger
from typing import Dict, Any, List
import asyncio
import traceback
from datetime import datetime

from app.services.resume_parser import ResumeParser
from app.services.document_parser import DocumentParser
from app.core.database import SessionLocal
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.schemas.resume import ResumeStatus

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def process_resume(self, resume_id: int) -> Dict[str, Any]:
    """
    Process a single resume file - extract text, parse data, and update database
    """
    try:
        logger.info(f"Starting resume processing for ID: {resume_id}")
        
        # Update task progress
        self.update_state(state='PROGRESS', meta={'step': 'initializing', 'progress': 0})
        
        with SessionLocal() as db:
            # Get resume from database
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                raise ValueError(f"Resume with ID {resume_id} not found")
            
            # Update status to processing
            resume.status = ResumeStatus.PROCESSING
            resume.processed_date = datetime.utcnow()
            db.commit()
            
            # Initialize parsers
            document_parser = DocumentParser()
            resume_parser = ResumeParser()
            
            # Step 1: Extract text from document
            self.update_state(state='PROGRESS', meta={'step': 'extracting_text', 'progress': 20})
            
            if resume.file_type.lower() == 'pdf':
                extracted_text = document_parser.extract_text_from_pdf(resume.file_path)
            elif resume.file_type.lower() in ['doc', 'docx']:
                extracted_text = document_parser.extract_text_from_docx(resume.file_path)
            else:
                raise ValueError(f"Unsupported file type: {resume.file_type}")
            
            # Step 2: Parse resume data
            self.update_state(state='PROGRESS', meta={'step': 'parsing_data', 'progress': 50})
            
            # Run async parsing in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                parsed_resume = loop.run_until_complete(
                    resume_parser.parse_resume(extracted_text)
                )
            finally:
                loop.close()
            
            # Step 3: Update database
            self.update_state(state='PROGRESS', meta={'step': 'updating_database', 'progress': 80})
            
            # Update resume record
            resume.extracted_text = extracted_text
            resume.structured_data = {
                'contact_info': parsed_resume.contact_info.__dict__,
                'summary': parsed_resume.summary,
                'work_experience': [exp.__dict__ for exp in parsed_resume.work_experience],
                'education': [edu.__dict__ for edu in parsed_resume.education],
                'skills': parsed_resume.skills,
                'certifications': parsed_resume.certifications,
                'languages': parsed_resume.languages,
                'projects': parsed_resume.projects,
                'achievements': parsed_resume.achievements,
                'processing_metadata': parsed_resume.processing_metadata
            }
            resume.status = ResumeStatus.COMPLETED
            
            # Create or update candidate record
            candidate = db.query(Candidate).filter(Candidate.resume_id == resume_id).first()
            if not candidate:
                candidate = Candidate(resume_id=resume_id)
                db.add(candidate)
            
            # Update candidate information
            candidate.full_name = parsed_resume.contact_info.full_name
            candidate.email = parsed_resume.contact_info.email
            candidate.phone = parsed_resume.contact_info.phone
            candidate.location = parsed_resume.contact_info.address
            candidate.years_experience = parsed_resume.processing_metadata.get('total_years_experience', 0)
            candidate.skills = parsed_resume.skills
            candidate.work_history = [exp.__dict__ for exp in parsed_resume.work_experience]
            candidate.certifications = parsed_resume.certifications
            
            db.commit()
            
            # Complete task
            self.update_state(state='PROGRESS', meta={'step': 'completed', 'progress': 100})
            
            logger.info(f"Successfully processed resume ID: {resume_id}")
            
            return {
                'status': 'success',
                'resume_id': resume_id,
                'candidate_name': parsed_resume.contact_info.full_name,
                'skills_found': len(parsed_resume.skills.get('skills', [])),
                'work_experience_years': parsed_resume.processing_metadata.get('total_years_experience', 0),
                'processing_time': (datetime.utcnow() - resume.processed_date).total_seconds()
            }
            
    except Exception as exc:
        logger.error(f"Error processing resume {resume_id}: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Update resume status to failed
        try:
            with SessionLocal() as db:
                resume = db.query(Resume).filter(Resume.id == resume_id).first()
                if resume:
                    resume.status = ResumeStatus.FAILED
                    db.commit()
        except Exception:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying resume processing for ID: {resume_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        
        return {
            'status': 'failed',
            'resume_id': resume_id,
            'error': str(exc)
        }


@shared_task(bind=True)
def bulk_process_resumes(self, resume_ids: List[int]) -> Dict[str, Any]:
    """
    Process multiple resumes in bulk
    """
    try:
        logger.info(f"Starting bulk processing for {len(resume_ids)} resumes")
        
        results = []
        total_count = len(resume_ids)
        
        for i, resume_id in enumerate(resume_ids):
            self.update_state(
                state='PROGRESS', 
                meta={
                    'step': f'processing_resume_{resume_id}',
                    'progress': int((i / total_count) * 100),
                    'current_resume': resume_id,
                    'completed': i,
                    'total': total_count
                }
            )
            
            # Process individual resume
            result = process_resume.apply_async(args=[resume_id])
            results.append({
                'resume_id': resume_id,
                'task_id': result.id,
                'status': 'queued'
            })
        
        logger.info(f"Queued {len(results)} resume processing tasks")
        
        return {
            'status': 'success',
            'total_resumes': total_count,
            'queued_tasks': len(results),
            'task_results': results
        }
        
    except Exception as exc:
        logger.error(f"Error in bulk resume processing: {str(exc)}")
        return {
            'status': 'failed',
            'error': str(exc)
        }
