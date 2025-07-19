from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime
import asyncio
import json

from app.core.database import get_db
from app.schemas.resume import (
    Resume, ResumeCreate, ResumeUpdate, ResumeList, 
    ResumeUploadResponse, ResumeProcessingStatus, BulkResumeUpload
)
from app.services.resume_parser import ResumeParser
from app.services.document_validator import DocumentValidator
from app.models.resume import Resume as ResumeModel
from app.models.candidate import Candidate as CandidateModel

router = APIRouter()

# Initialize services
resume_parser = ResumeParser()
document_validator = DocumentValidator()

# Upload directory configuration
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a single resume file for processing.
    
    - **file**: Resume file (PDF, DOC, DOCX)
    - Returns: Upload confirmation with processing status
    """
    try:
        # Basic file validation before saving
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1]
        if file_extension.lower() not in ['.pdf', '.doc', '.docx']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only PDF, DOC, and DOCX files are allowed."
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate saved file
        validation_result = document_validator.validate_file(file_path, file.filename)
        if not validation_result['is_valid']:
            # Clean up the saved file if validation fails
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file: {', '.join(validation_result['errors'])}"
            )
        
        # Create resume record
        resume_data = ResumeCreate(
            filename=file.filename,
            file_type=file_extension[1:],
            file_size=len(content),
            file_path=file_path
        )
        
        # Save to database
        db_resume = ResumeModel(
            filename=resume_data.filename,
            file_type=resume_data.file_type,
            file_size=resume_data.file_size,
            file_path=resume_data.file_path,
            status="pending"
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        # Start background processing
        asyncio.create_task(process_resume_background(db_resume.id, file_path))
        
        return ResumeUploadResponse(
            id=db_resume.id,
            filename=db_resume.filename,
            file_size=db_resume.file_size,
            status=db_resume.status,
            upload_date=db_resume.upload_date
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/bulk-upload", response_model=BulkResumeUpload)
async def bulk_upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple resume files for batch processing.
    
    - **files**: List of resume files (PDF, DOC, DOCX)
    - Returns: Bulk upload results with success/failure counts
    """
    successful = []
    failed = []
    
    for file in files:
        try:
            # Basic file validation before saving
            if not file.filename:
                failed.append({
                    "filename": "unnamed_file",
                    "error": "No filename provided"
                })
                continue
            
            # Check file extension
            file_extension = os.path.splitext(file.filename)[1]
            if file_extension.lower() not in ['.pdf', '.doc', '.docx']:
                failed.append({
                    "filename": file.filename,
                    "error": "Invalid file type. Only PDF, DOC, and DOCX files are allowed."
                })
                continue
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Validate saved file
            validation_result = document_validator.validate_file(file_path, file.filename)
            if not validation_result['is_valid']:
                # Clean up the saved file if validation fails
                os.remove(file_path)
                failed.append({
                    "filename": file.filename,
                    "error": ', '.join(validation_result['errors'])
                })
                continue
            
            # Create resume record
            db_resume = ResumeModel(
                filename=file.filename,
                file_type=file_extension[1:],
                file_size=len(content),
                file_path=file_path,
                status="pending"
            )
            
            db.add(db_resume)
            db.commit()
            db.refresh(db_resume)
            
            # Start background processing
            asyncio.create_task(process_resume_background(db_resume.id, file_path))
            
            successful.append(ResumeUploadResponse(
                id=db_resume.id,
                filename=db_resume.filename,
                file_size=db_resume.file_size,
                status=db_resume.status,
                upload_date=db_resume.upload_date
            ))
            
        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return BulkResumeUpload(
        successful=successful,
        failed=failed,
        total_uploaded=len(successful),
        total_failed=len(failed)
    )

@router.get("/", response_model=ResumeList)
async def list_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all resumes with pagination and filtering.
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **status**: Filter by processing status
    - Returns: Paginated list of resumes
    """
    query = db.query(ResumeModel)
    
    if status:
        query = query.filter(ResumeModel.status == status)
    
    total = query.count()
    resumes = query.offset(skip).limit(limit).all()
    
    return ResumeList(
        items=[Resume.model_validate(resume) for resume in resumes],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{resume_id}", response_model=Resume)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific resume by ID.
    
    - **resume_id**: ID of the resume to retrieve
    - Returns: Resume details with processing results
    """
    resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return Resume.model_validate(resume)

@router.get("/{resume_id}/status", response_model=ResumeProcessingStatus)
async def get_resume_status(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get processing status of a specific resume.
    
    - **resume_id**: ID of the resume
    - Returns: Processing status and progress
    """
    resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Calculate progress based on status
    progress_map = {
        "pending": 0.0,
        "processing": 50.0,
        "completed": 100.0,
        "failed": 0.0
    }
    
    return ResumeProcessingStatus(
        id=resume.id,
        filename=resume.filename,
        status=resume.status,
        processed_date=resume.processed_date,
        processing_errors=resume.processing_errors,
        progress=progress_map.get(resume.status, 0.0)
    )

@router.put("/{resume_id}", response_model=Resume)
async def update_resume(
    resume_id: int,
    resume_update: ResumeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update resume information.
    
    - **resume_id**: ID of the resume to update
    - **resume_update**: Updated resume data
    - Returns: Updated resume
    """
    resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Update fields
    update_data = resume_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)
    
    resume.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(resume)
    
    return Resume.model_validate(resume)

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a resume and its associated file.
    
    - **resume_id**: ID of the resume to delete
    - Returns: Deletion confirmation
    """
    resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file if it exists
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}

@router.post("/{resume_id}/reprocess")
async def reprocess_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Reprocess a resume that failed or needs updating.
    
    - **resume_id**: ID of the resume to reprocess
    - Returns: Reprocessing confirmation
    """
    resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=400, detail="Resume file not found")
    
    # Reset status and start processing
    resume.status = "pending"
    resume.processed_date = None
    resume.processing_errors = None
    resume.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Start background processing
    asyncio.create_task(process_resume_background(resume.id, resume.file_path))
    
    return {"message": "Resume reprocessing started"}

async def process_resume_background(resume_id: int, file_path: str):
    """Background task for resume processing"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get resume record
        resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        if not resume:
            return
        
        # Update status to processing
        resume.status = "processing"
        resume.updated_at = datetime.utcnow()
        db.commit()
        
        # Process the resume
        try:
            parsed_resume = resume_parser.parse_resume(file_path)
            
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
                candidate = CandidateModel(
                    full_name=parsed_resume.contact_info.full_name,
                    email=parsed_resume.contact_info.email,
                    phone=parsed_resume.contact_info.phone,
                    location=parsed_resume.contact_info.location,
                    resume_id=resume.id
                )
                db.add(candidate)
            
        except Exception as e:
            resume.status = "failed"
            resume.processing_errors = {"error": str(e)}
        
        resume.updated_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()
