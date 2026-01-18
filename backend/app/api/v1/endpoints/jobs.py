from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio

from app.core.database import get_db
from app.schemas.job_description import (
    JobDescription, JobDescriptionCreate, JobDescriptionUpdate, 
    JobDescriptionList, BulkJobDescriptionCreate
)
from app.services.job_scraper import JobScraper
from app.services.semantic_skills import semantic_skills_extractor
from app.models.job_description import JobDescription as JobDescriptionModel
from app.models.match import Match as MatchModel

router = APIRouter()

# Service instances will be created on-demand to avoid startup delays

@router.post("/", response_model=JobDescription)
async def create_job_description(
    job_data: JobDescriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job description.
    
    - **job_data**: Job description data
    - Returns: Created job description
    """
    try:
        # Create job description record
        db_job = JobDescriptionModel(
            title=job_data.title,
            company=job_data.company,
            description=job_data.description,
            source=job_data.source,
            location=job_data.location,
            salary_range=job_data.salary_range,
            employment_type=job_data.employment_type,
            experience_level=job_data.experience_level,
            scraped_date=job_data.scraped_date,
            processed_date=job_data.processed_date,
            requirements=job_data.requirements,
            source_url=job_data.source_url,
            status=job_data.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        # Start background processing to extract skills
        asyncio.create_task(process_job_background(db_job.id))
        
        return JobDescription.model_validate(db_job)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")

@router.post("/bulk", response_model=BulkJobDescriptionCreate)
async def bulk_create_job_descriptions(
    jobs_data: List[JobDescriptionCreate],
    db: Session = Depends(get_db)
):
    """
    Create multiple job descriptions in bulk.
    
    - **jobs_data**: List of job description data
    - Returns: Bulk creation results
    """
    successful = []
    failed = []
    
    for job_data in jobs_data:
        try:
            db_job = JobDescriptionModel(
                title=job_data.title,
                company=job_data.company,
                description=job_data.description,
                source=job_data.source,
                location=job_data.location,
                salary_range=job_data.salary_range,
                employment_type=job_data.employment_type,
                experience_level=job_data.experience_level,
                scraped_date=job_data.scraped_date,
                processed_date=job_data.processed_date,
                requirements=job_data.requirements,
                source_url=job_data.source_url,
                status=job_data.status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            
            # Start background processing
            asyncio.create_task(process_job_background(db_job.id))
            
            successful.append(JobDescription.model_validate(db_job))
            
        except Exception as e:
            failed.append({
                "title": job_data.title,
                "company": job_data.company,
                "error": str(e)
            })
    
    return BulkJobDescriptionCreate(
        successful=successful,
        failed=failed,
        total_created=len(successful),
        total_failed=len(failed)
    )

@router.get("/", response_model=JobDescriptionList)
async def list_job_descriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List job descriptions with pagination and filtering.
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **company**: Filter by company name
    - **location**: Filter by location
    - **employment_type**: Filter by employment type
    - **experience_level**: Filter by experience level
    - **status**: Filter by status
    - Returns: Paginated list of job descriptions
    """
    query = db.query(JobDescriptionModel)
    
    # Apply filters
    if company:
        query = query.filter(JobDescriptionModel.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(JobDescriptionModel.location.ilike(f"%{location}%"))
    if employment_type:
        query = query.filter(JobDescriptionModel.employment_type == employment_type)
    if experience_level:
        query = query.filter(JobDescriptionModel.experience_level == experience_level)
    if status:
        query = query.filter(JobDescriptionModel.status == status)
    
    total = query.count()
    jobs = query.offset(skip).limit(limit).all()
    
    return JobDescriptionList(
        items=[JobDescription.model_validate(job) for job in jobs],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{job_id}", response_model=JobDescription)
async def get_job_description(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific job description by ID.
    
    - **job_id**: ID of the job description
    - Returns: Job description details
    """
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return JobDescription.model_validate(job)

@router.put("/{job_id}", response_model=JobDescription)
async def update_job_description(
    job_id: int,
    job_update: JobDescriptionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a job description.
    
    - **job_id**: ID of the job description to update
    - **job_update**: Updated job description data
    - Returns: Updated job description
    """
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Update fields
    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    job.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job)
    
    return JobDescription.model_validate(job)

@router.delete("/{job_id}")
async def delete_job_description(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a job description.
    
    - **job_id**: ID of the job description to delete
    - Returns: Deletion confirmation
    """
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # First, delete all matches associated with this job
    db.query(MatchModel).filter(MatchModel.job_id == job_id).delete()
    
    # Then, delete the job description
    db.delete(job)
    db.commit()
    
    return {"message": "Job description deleted successfully"}

@router.post("/{job_id}/reprocess")
async def reprocess_job_description(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Reprocess a job description to extract skills and structure data.
    
    - **job_id**: ID of the job description to reprocess
    - Returns: Reprocessing confirmation
    """
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Reset processing fields
    job.processed_date = None
    job.structured_data = None
    job.extracted_skills = None
    job.processing_errors = None
    job.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Start background processing
    asyncio.create_task(process_job_background(job.id))
    
    return {"message": "Job description reprocessing started"}

@router.get("/{job_id}/skills")
async def get_job_skills(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get extracted skills for a job description.
    
    - **job_id**: ID of the job description
    - Returns: Extracted skills information
    """
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return {
        "job_id": job.id,
        "title": job.title,
        "company": job.company,
        "extracted_skills": job.extracted_skills,
        "processed_date": job.processed_date
    }

@router.post("/scrape")
async def scrape_job_descriptions(
    urls: List[str],
    db: Session = Depends(get_db)
):
    """
    Scrape job descriptions from provided URLs.
    
    - **urls**: List of job posting URLs to scrape
    - Returns: Scraping results
    """
    try:
        scraped_jobs = []
        failed_urls = []
        
        for url in urls:
            try:
                # Initialize job scraper on-demand
                job_scraper = JobScraper()
                # Scrape job description
                job_data = job_scraper.scrape_job(url)
                
                # Create job description record
                db_job = JobDescriptionModel(
                    title=job_data.title,
                    company=job_data.company,
                    description=job_data.description,
                    source="scraped",
                    location=job_data.location,
                    salary_range=job_data.salary_range,
                    employment_type=job_data.employment_type,
                    experience_level=job_data.experience_level,
                    scraped_date=datetime.utcnow(),
                    requirements=job_data.requirements,
                    source_url=url,
                    status="active",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(db_job)
                db.commit()
                db.refresh(db_job)
                
                # Start background processing
                asyncio.create_task(process_job_background(db_job.id))
                
                scraped_jobs.append(JobDescription.model_validate(db_job))
                
            except Exception as e:
                failed_urls.append({
                    "url": url,
                    "error": str(e)
                })
        
        return {
            "successful": scraped_jobs,
            "failed": failed_urls,
            "total_scraped": len(scraped_jobs),
            "total_failed": len(failed_urls)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/search/skills")
async def search_jobs_by_skills(
    skills: str = Query(..., description="Comma-separated list of skills"),
    min_matches: int = Query(1, ge=1, description="Minimum number of skill matches"),
    db: Session = Depends(get_db)
):
    """
    Search job descriptions by required skills.
    
    - **skills**: Comma-separated list of skills to search for
    - **min_matches**: Minimum number of skills that must match
    - Returns: Matching job descriptions
    """
    try:
        skill_list = [skill.strip().lower() for skill in skills.split(",")]
        
        # Query jobs and filter by skills
        jobs = db.query(JobDescriptionModel).filter(
            JobDescriptionModel.extracted_skills.isnot(None)
        ).all()
        
        matching_jobs = []
        for job in jobs:
            if job.extracted_skills and 'skills' in job.extracted_skills:
                job_skills = [skill.lower() for skill in job.extracted_skills['skills']]
                matches = len(set(skill_list) & set(job_skills))
                
                if matches >= min_matches:
                    job_dict = JobDescription.model_validate(job).model_dump()
                    job_dict['skill_matches'] = matches
                    job_dict['matched_skills'] = list(set(skill_list) & set(job_skills))
                    matching_jobs.append(job_dict)
        
        # Sort by number of matches (descending)
        matching_jobs.sort(key=lambda x: x['skill_matches'], reverse=True)
        
        return {
            "jobs": matching_jobs,
            "total_matches": len(matching_jobs),
            "searched_skills": skill_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

async def process_job_background(job_id: int):
    """Background task for job description processing"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get job record
        job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
        if not job:
            return
        
        # Process the job description
        try:
            # Extract skills from job description
            full_text = f"{job.description} {job.requirements or ''}"
            # Use semantic skills extractor
            extracted_skills = semantic_skills_extractor.extract_skills(full_text)
            
            # Update job with extracted data
            job.extracted_skills = {
                "skills": extracted_skills,
                "extraction_date": datetime.utcnow().isoformat(),
                "source_text_length": len(full_text)
            }
            
            # Create structured data
            job.structured_data = {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "employment_type": job.employment_type,
                "experience_level": job.experience_level,
                "salary_range": job.salary_range,
                "skills": extracted_skills,
                "processed_date": datetime.utcnow().isoformat()
            }
            
            job.processed_date = datetime.utcnow()
            
        except Exception as e:
            job.processing_errors = {"error": str(e)}
        
        job.updated_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()
