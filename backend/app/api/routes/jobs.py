from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import JobDescription
from app.schemas.common import build_page
from app.schemas.job import (
    JobDescriptionBase,
    JobDescriptionCreate,
    JobDescriptionUpdate,
    JobListResponse,
    JobSearchBySkillsResponse,
    JobSearchMatch,
    JobSkillsResponse,
)
from app.services.embedding_service import cached_encode, get_embedding_provider
from app.services.job_service import process_job_payload, search_jobs_by_skills as service_search_jobs_by_skills
from app.services.text_processing import dedupe_preserve_order

logger = logging.getLogger(__name__)
router = APIRouter()
embedder = get_embedding_provider()


def _apply_job_processing(job: JobDescription) -> None:
    try:
        processed = process_job_payload(job.title, job.description, job.requirements)
        job.structured_data = processed["structured_data"]
        job.extracted_skills = processed["extracted_skills"]
        job.embedding = cached_encode(
            embedder,
            "\n".join(part for part in [job.title, job.description, job.requirements or ""] if part),
        )
        job.processed_date = datetime.now(timezone.utc)
        job.processing_errors = None
    except Exception as exc:
        job.processing_errors = {"message": str(exc)}
        logger.exception("Job processing failed for job %s", job.id)


@router.post("/", response_model=JobDescriptionBase, status_code=201)
def create_job(payload: JobDescriptionCreate, db: Session = Depends(get_db)) -> JobDescriptionBase:
    job = JobDescription(**payload.model_dump())
    _apply_job_processing(job)
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobDescriptionBase.model_validate(job)


@router.get("/", response_model=JobListResponse)
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: str | None = Query(None),
    location: str | None = Query(None),
    employment_type: str | None = Query(None),
    experience_level: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
) -> JobListResponse:
    query = db.query(JobDescription)
    if company:
        query = query.filter(JobDescription.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(JobDescription.location.ilike(f"%{location}%"))
    if employment_type:
        query = query.filter(JobDescription.employment_type == employment_type)
    if experience_level:
        query = query.filter(JobDescription.experience_level == experience_level)
    if status:
        query = query.filter(JobDescription.status == status)
    total = query.count()
    items = [
        JobDescriptionBase.model_validate(item)
        for item in query.order_by(JobDescription.id.desc()).offset(skip).limit(limit)
    ]
    return build_page(items=items, total=total, skip=skip, limit=limit)


@router.get("/search/skills", response_model=JobSearchBySkillsResponse)
def search_jobs_by_skills(
    skills: str = Query(...),
    min_matches: int = Query(1, ge=1),
    db: Session = Depends(get_db),
) -> JobSearchBySkillsResponse:
    searched_skills = dedupe_preserve_order(skills.split(","))
    matches = [
        JobSearchMatch(**item)
        for item in service_search_jobs_by_skills(db, searched_skills, min_matches)
    ]
    return JobSearchBySkillsResponse(
        jobs=matches,
        total_matches=len(matches),
        searched_skills=searched_skills,
    )


@router.get("/{job_id}", response_model=JobDescriptionBase)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobDescriptionBase:
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JobDescriptionBase.model_validate(job)


@router.get("/{job_id}/skills", response_model=JobSkillsResponse)
def get_job_skills(job_id: int, db: Session = Depends(get_db)) -> JobSkillsResponse:
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JobSkillsResponse(
        job_id=job.id,
        title=job.title,
        company=job.company,
        extracted_skills=job.extracted_skills,
        processed_date=job.processed_date,
    )


@router.put("/{job_id}", response_model=JobDescriptionBase)
def update_job(job_id: int, payload: JobDescriptionUpdate, db: Session = Depends(get_db)) -> JobDescriptionBase:
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    content_fields = {"title", "description", "requirements"}
    if content_fields & set(payload.model_dump(exclude_unset=True).keys()):
        _apply_job_processing(job)
    db.commit()
    db.refresh(job)
    return JobDescriptionBase.model_validate(job)


@router.post("/{job_id}/reprocess")
def reprocess_job(job_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    _apply_job_processing(job)
    db.commit()
    db.refresh(job)
    return {"message": "Job description reprocessing completed"}


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    db.delete(job)
    db.commit()
    return {"message": "Job description deleted successfully"}
