from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import JobDescription
from app.schemas.common import build_page
from app.schemas.job import (
    BulkJobScrapeResponse,
    JobDescriptionBase,
    JobDescriptionCreate,
    JobDescriptionUpdate,
    JobListResponse,
    JobSearchBySkillsResponse,
    JobSearchMatch,
    JobSkillsResponse,
    ScrapeJobsRequest,
)
from app.services.embedding_service import get_embedding_provider
from app.services.job_scraper import scrape_job_url
from app.services.job_service import process_job_payload
from app.services.text_processing import dedupe_preserve_order, keyword_overlap_score

router = APIRouter()
embedder = get_embedding_provider()


def _apply_job_processing(job: JobDescription) -> None:
    processed = process_job_payload(job.title, job.description, job.requirements)
    job.structured_data = processed["structured_data"]
    job.extracted_skills = processed["extracted_skills"]
    job.embedding = embedder.encode(
        "\n".join(part for part in [job.title, job.description, job.requirements or ""] if part)
    )
    job.processed_date = datetime.now(timezone.utc)
    job.processing_errors = None


@router.post("/", response_model=JobDescriptionBase)
def create_job(payload: JobDescriptionCreate, db: Session = Depends(get_db)):
    job = JobDescription(**payload.model_dump())
    _apply_job_processing(job)
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobDescriptionBase.model_validate(job)


@router.post("/scrape", response_model=BulkJobScrapeResponse)
def scrape_jobs(payload: ScrapeJobsRequest | list[str] = Body(...), db: Session = Depends(get_db)):
    urls = payload.urls if isinstance(payload, ScrapeJobsRequest) else payload
    successful: list[JobDescriptionBase] = []
    failed: list[dict[str, str]] = []
    for url in urls:
        try:
            scraped = scrape_job_url(url)
            job = JobDescription(
                title=scraped["title"],
                company="Unknown Company",
                description=scraped["description"],
                source="scraped",
                source_url=url,
                status="active",
            )
            _apply_job_processing(job)
            db.add(job)
            db.commit()
            db.refresh(job)
            successful.append(JobDescriptionBase.model_validate(job))
        except Exception as exc:
            failed.append({"url": url, "error": str(exc)})
    return BulkJobScrapeResponse(
        successful=successful,
        failed=failed,
        total_scraped=len(successful),
        total_failed=len(failed),
    )


@router.get("/search/skills", response_model=JobSearchBySkillsResponse)
def search_jobs_by_skills(
    skills: str = Query(...),
    min_matches: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    searched_skills = dedupe_preserve_order(skills.split(","))
    matches: list[JobSearchMatch] = []
    for job in db.query(JobDescription).all():
        _, matched, _ = keyword_overlap_score(job.extracted_skills or [], searched_skills)
        if len(matched) >= min_matches:
            matches.append(
                JobSearchMatch(
                    id=job.id,
                    title=job.title,
                    company=job.company,
                    skill_matches=len(matched),
                    matched_skills=matched,
                )
            )
    return JobSearchBySkillsResponse(
        jobs=matches,
        total_matches=len(matches),
        searched_skills=searched_skills,
    )


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
):
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
    items = [JobDescriptionBase.model_validate(item) for item in query.order_by(JobDescription.id.desc()).offset(skip).limit(limit)]
    return build_page(items=items, total=total, skip=skip, limit=limit)


@router.get("/{job_id}/skills", response_model=JobSkillsResponse)
def get_job_skills(job_id: int, db: Session = Depends(get_db)):
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


@router.post("/{job_id}/reprocess")
def reprocess_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    _apply_job_processing(job)
    db.commit()
    db.refresh(job)
    return {"message": "Job description reprocessing started"}


@router.get("/{job_id}", response_model=JobDescriptionBase)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JobDescriptionBase.model_validate(job)


@router.put("/{job_id}", response_model=JobDescriptionBase)
def update_job(job_id: int, payload: JobDescriptionUpdate, db: Session = Depends(get_db)):
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    _apply_job_processing(job)
    db.commit()
    db.refresh(job)
    return JobDescriptionBase.model_validate(job)


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    db.delete(job)
    db.commit()
    return {"message": "Job description deleted successfully"}
