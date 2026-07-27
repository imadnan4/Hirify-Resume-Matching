from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.schemas.candidate import (
    CandidateBase,
    CandidateListBase,
    CandidateListResponse,
    CandidateResumeResponse,
    CandidateSearchBySkillsResponse,
    CandidateSkillMatch,
    CandidateUpdate,
)
from app.schemas.common import build_page
from app.services.candidate_service import search_candidates_by_skills
from app.services.text_processing import dedupe_preserve_order

router = APIRouter()


@router.get("/search/by-skills", response_model=CandidateSearchBySkillsResponse)
def search_by_skills(
    skills: str = Query(...),
    min_matches: int = Query(1, ge=1),
    db: Session = Depends(get_db),
) -> CandidateSearchBySkillsResponse:
    searched_skills = dedupe_preserve_order(skills.split(","))
    matches = [CandidateSkillMatch(**item) for item in search_candidates_by_skills(db, searched_skills, min_matches)]
    return CandidateSearchBySkillsResponse(
        candidates=matches,
        total_matches=len(matches),
        searched_skills=searched_skills,
    )


@router.get("/", response_model=CandidateListResponse)
def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> CandidateListResponse:
    query = db.query(Candidate)
    total = query.count()
    items = [CandidateListBase.model_validate(item) for item in query.order_by(Candidate.id.desc()).offset(skip).limit(limit)]
    return build_page(items=items, total=total, skip=skip, limit=limit)


@router.get("/{candidate_id}/resume", response_model=CandidateResumeResponse)
def get_candidate_resume(candidate_id: int, db: Session = Depends(get_db)) -> CandidateResumeResponse:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    resume = db.get(Resume, candidate.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return CandidateResumeResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.full_name,
        resume_id=resume.id,
        resume_filename=resume.filename,
        resume_status=resume.status,
        processed_date=resume.processed_date,
        structured_data=resume.structured_data,
    )


@router.get("/{candidate_id}", response_model=CandidateBase)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)) -> CandidateBase:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateBase.model_validate(candidate)


@router.put("/{candidate_id}", response_model=CandidateBase)
def update_candidate(candidate_id: int, payload: CandidateUpdate, db: Session = Depends(get_db)) -> CandidateBase:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)
    db.commit()
    db.refresh(candidate)
    return CandidateBase.model_validate(candidate)


@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully"}
