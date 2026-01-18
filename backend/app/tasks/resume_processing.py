"""
Celery tasks for resume processing.
"""

from celery import current_task
from datetime import datetime
from typing import Dict, Any
import json

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.resume import Resume as ResumeModel
from app.models.candidate import Candidate as CandidateModel
from app.services.resume_parser import ResumeParser
from app.services.document_text_extractor import DocumentTextExtractor


@celery_app.task(bind=True)
def process_resume_task(self, resume_id: int, file_path: str) -> Dict[str, Any]:
    """
    Process a resume file in the background.
    
    Args:
        resume_id: Database ID of the resume record
        file_path: Path to the resume file
        
    Returns:
        Dict containing processing results
    """
    db = SessionLocal()
    
    try:
        # Get resume record
        resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        if not resume:
            return {"error": "Resume not found"}
        
        # Update status to processing
        resume.status = "processing"
        resume.updated_at = datetime.utcnow()
        db.commit()
        
        # Update task progress
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': 'Starting resume parsing...'}
        )
        
        # Process the resume
        try:
            # Extract text from the document file first
            document_extractor = DocumentTextExtractor()
            
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 30, 'total': 100, 'status': 'Extracting text from document...'}
            )
            
            # Extract text from the file
            extraction_result = document_extractor.extract_text(file_path)
            extracted_text = extraction_result.get('text', '')
            
            if not extracted_text:
                raise Exception("No text could be extracted from the document")
            
            # Initialize parser on-demand to avoid startup delays
            resume_parser = ResumeParser()
            
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 60, 'total': 100, 'status': 'Parsing resume content...'}
            )
            
            # Parse the extracted text (not the file path)
            parsed_resume = resume_parser.parse_resume(extracted_text)
            
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 75, 'total': 100, 'status': 'Structuring data...'}
            )
            
            # Update resume with parsed data
            resume.extracted_text = parsed_resume.raw_text
            resume.structured_data = {
                "contact_info": parsed_resume.contact_info.__dict__,
                "work_experience": [exp.__dict__ for exp in parsed_resume.work_experience],
                "education": [edu.__dict__ for edu in parsed_resume.education],
                "skills": parsed_resume.skills,
                "certifications": parsed_resume.certifications,
                "summary": parsed_resume.summary,
                "processing_metadata": parsed_resume.processing_metadata
            }
            resume.status = "completed"
            resume.processed_date = datetime.utcnow()
            
            # Create candidate record if name is available
            if parsed_resume.contact_info.full_name:
                existing_candidate = db.query(CandidateModel).filter(
                    CandidateModel.resume_id == resume.id
                ).first()
                
                if not existing_candidate:
                    candidate = CandidateModel(
                        full_name=parsed_resume.contact_info.full_name,
                        email=parsed_resume.contact_info.email,
                        phone=parsed_resume.contact_info.phone,
                        location=parsed_resume.contact_info.location,
                        resume_id=resume.id
                    )
                    db.add(candidate)
            
            current_task.update_state(
                state='PROGRESS',
                meta={'current': 100, 'total': 100, 'status': 'Processing completed'}
            )
            
            result = {
                "status": "completed",
                "resume_id": resume_id,
                "extracted_text_length": len(parsed_resume.raw_text) if parsed_resume.raw_text else 0,
                "skills_count": len(parsed_resume.skills),
                "experience_count": len(parsed_resume.work_experience),
                "education_count": len(parsed_resume.education)
            }
            
        except Exception as e:
            resume.status = "failed"
            resume.processing_errors = {"error": str(e), "task_id": self.request.id}
            result = {
                "status": "failed",
                "resume_id": resume_id,
                "error": str(e)
            }
        
        resume.updated_at = datetime.utcnow()
        db.commit()
        
        return result
        
    except Exception as e:
        # Handle database errors
        return {
            "status": "failed",
            "resume_id": resume_id,
            "error": f"Database error: {str(e)}"
        }
        
    finally:
        db.close()


@celery_app.task
def cleanup_failed_uploads():
    """
    Periodic task to clean up failed uploads and orphaned files.
    """
    import os
    from datetime import timedelta
    
    db = SessionLocal()
    
    try:
        # Find resumes that have been stuck in "pending" status for more than 1 hour
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        stuck_resumes = db.query(ResumeModel).filter(
            ResumeModel.status == "pending",
            ResumeModel.created_at < cutoff_time
        ).all()
        
        cleaned_count = 0
        for resume in stuck_resumes:
            # Mark as failed
            resume.status = "failed"
            resume.processing_errors = {
                "error": "Processing timeout - stuck in pending status",
                "cleanup_date": datetime.utcnow().isoformat()
            }
            resume.updated_at = datetime.utcnow()
            cleaned_count += 1
            
        db.commit()
        
        return {
            "cleaned_resumes": cleaned_count,
            "cutoff_time": cutoff_time.isoformat()
        }
        
    finally:
        db.close()
