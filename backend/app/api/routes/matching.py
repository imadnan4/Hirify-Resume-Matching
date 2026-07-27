from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.job import JobDescription
from app.models.match import Match
from app.models.resume import Resume
from app.schemas.common import build_page
from app.schemas.match import (
    BulkMatchRequest,
    BulkMatchResponse,
    MatchBase,
    MatchExplanationResponse,
    MatchListResponse,
    MatchStatsResponse,
    MatchSummary,
    MatchUpdate,
    RankedCandidateResponse,
    SingleMatchRequest,
)
from app.schemas.resume import ResumePreviewResponse
from app.services.matching_service import MatchComputation, matching_service

router = APIRouter()


def _build_computation(*, resume: Resume, job: JobDescription) -> MatchComputation:
    if resume.status != "completed" or not resume.extracted_text:
        raise HTTPException(status_code=400, detail="Resume not processed yet")
    preview = ResumePreviewResponse.model_validate(resume.structured_data or {})
    return matching_service.compute_match(
        resume_text=resume.extracted_text,
        resume_preview=preview,
        job_title=job.title,
        job_description=job.description,
        job_requirements=job.requirements,
        job_skills=job.extracted_skills,
        job_structured_data=job.structured_data,
    )


def _persist_match(
    db: Session,
    *,
    resume: Resume,
    job: JobDescription,
    computation: MatchComputation,
    existing_lookup: dict[tuple[int, int], Match] | None = None,
) -> tuple[Match, MatchSummary]:
    if existing_lookup is not None:
        match = existing_lookup.get((resume.id, job.id))
    else:
        match = (
            db.query(Match)
            .filter(Match.resume_id == resume.id, Match.job_id == job.id)
            .first()
        )
    if match is None:
        match = Match(resume_id=resume.id, job_id=job.id)
        db.add(match)
    match.overall_score = computation.overall_score
    match.skills_score = computation.skills_score
    match.experience_score = computation.experience_score
    match.education_score = computation.education_score
    match.additional_score = computation.additional_score
    match.matched_skills = computation.matched_skills
    match.missing_skills = computation.missing_skills
    match.skill_overlap_count = computation.skill_overlap_count
    match.total_required_skills = computation.total_required_skills
    match.explanation = computation.explanation
    match.confidence_level = computation.confidence_level
    match.recommendation = computation.recommendation
    resume.embedding = computation.resume_embedding
    job.embedding = computation.job_embedding
    summary = MatchSummary(
        resume_id=resume.id,
        job_id=job.id,
        overall_score=computation.overall_score,
        matched_skills=computation.matched_skills,
        missing_skills=computation.missing_skills,
        explanation=computation.explanation,
    )
    return match, summary


@router.post("/match", status_code=201)
def create_match(payload: SingleMatchRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    resume = db.get(Resume, payload.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    job = db.get(JobDescription, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    computation = _build_computation(resume=resume, job=job)
    match, summary = _persist_match(db, resume=resume, job=job, computation=computation)
    db.commit()
    db.refresh(match)
    return {
        "match_id": match.id,
        "overall_score": summary.overall_score,
        "scores": {
            "skills_match": match.skills_score,
            "experience_match": match.experience_score,
            "education_match": match.education_score,
            "additional_match": match.additional_score,
        },
        "matched_skills": summary.matched_skills,
        "missing_skills": summary.missing_skills,
        "explanation": match.explanation,
        "recommendation": match.recommendation,
    }


@router.post("/bulk-match", response_model=BulkMatchResponse)
def bulk_match(payload: BulkMatchRequest, db: Session = Depends(get_db)) -> BulkMatchResponse:
    started = perf_counter()
    resumes = {
        item.id: item
        for item in db.query(Resume)
        .filter(Resume.id.in_(payload.resume_ids))
        .all()
    }
    jobs = {
        item.id: item
        for item in db.query(JobDescription)
        .filter(JobDescription.id.in_(payload.job_ids))
        .all()
    }
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")
    if not jobs:
        raise HTTPException(status_code=404, detail="No job descriptions found")

    # Prefetch existing matches for all resume/job pairs to avoid N+1 queries
    existing_lookup: dict[tuple[int, int], Match] = {}
    if payload.resume_ids and payload.job_ids:
        existing = (
            db.query(Match)
            .filter(
                Match.resume_id.in_(payload.resume_ids),
                Match.job_id.in_(payload.job_ids),
            )
            .all()
        )
        existing_lookup = {(m.resume_id, m.job_id): m for m in existing}

    summaries: list[MatchSummary] = []
    for job_id in payload.job_ids:
        job = jobs.get(job_id)
        if not job:
            continue
        for resume_id in payload.resume_ids:
            resume = resumes.get(resume_id)
            if not resume or resume.status != "completed" or not resume.extracted_text:
                continue
            computation = _build_computation(resume=resume, job=job)
            if computation.overall_score < payload.min_score_threshold:
                continue
            _, summary = _persist_match(
                db, resume=resume, job=job, computation=computation,
                existing_lookup=existing_lookup,
            )
            if not payload.include_explanations:
                summary.explanation = None
            summaries.append(summary)
    db.commit()
    return BulkMatchResponse(
        total_matches=len(summaries),
        matches=summaries,
        processing_time_seconds=round(perf_counter() - started, 2),
    )


@router.get("/stats", response_model=MatchStatsResponse)
def get_match_stats(db: Session = Depends(get_db)) -> MatchStatsResponse:
    row = db.query(
        func.count(Match.id).label("total"),
        func.coalesce(func.round(func.avg(Match.overall_score), 4), 0.0).label("average"),
        func.count().filter(Match.overall_score >= 0.8).label("high"),
        func.count().filter(Match.overall_score < 0.4).label("low"),
    ).one()
    return MatchStatsResponse(
        total_matches=row.total,
        average_score=float(row.average),
        high_score_matches=row.high,
        low_score_matches=row.low,
    )


@router.get("/top-matches")
def get_top_matches(
    limit: int = Query(10, ge=1, le=100),
    job_id: int | None = Query(None),
    resume_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> list[MatchBase]:
    query = db.query(Match)
    if job_id is not None:
        query = query.filter(Match.job_id == job_id)
    if resume_id is not None:
        query = query.filter(Match.resume_id == resume_id)
    matches = query.order_by(Match.overall_score.desc()).limit(limit).all()
    return [MatchBase.model_validate(item) for item in matches]


@router.get("/job/{job_id}/candidates", response_model=list[RankedCandidateResponse])
def get_ranked_candidates(
    job_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RankedCandidateResponse]:
    job = db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    matches = (
        db.query(Match)
        .filter(Match.job_id == job_id)
        .order_by(Match.overall_score.desc())
        .limit(limit)
        .all()
    )
    resume_ids = [match.resume_id for match in matches]
    resume_map = {
        r.id: r
        for r in db.query(Resume)
        .options(selectinload(Resume.candidate))
        .filter(Resume.id.in_(resume_ids)).all()
    } if resume_ids else {}
    results: list[RankedCandidateResponse] = []
    for index, match in enumerate(matches, start=1):
        resume = resume_map.get(match.resume_id)
        candidate_name = None
        if resume and resume.candidate:
            candidate_name = resume.candidate.full_name
        elif resume and resume.structured_data:
            candidate_name = (resume.structured_data.get("contact_info") or {}).get("full_name")
        results.append(
            RankedCandidateResponse(
                rank=index,
                resume_id=match.resume_id,
                candidate_name=candidate_name,
                overall_score=match.overall_score,
                skills_score=match.skills_score,
                experience_score=match.experience_score,
                matched_skills=match.matched_skills or [],
                missing_skills=match.missing_skills or [],
                recommendation=match.recommendation,
            )
        )
    return results


@router.get("/", response_model=MatchListResponse)
def list_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resume_id: int | None = Query(None),
    job_id: int | None = Query(None),
    min_score: float | None = Query(None, ge=0, le=1),
    max_score: float | None = Query(None, ge=0, le=1),
    db: Session = Depends(get_db),
) -> MatchListResponse:
    query = db.query(Match)
    if resume_id is not None:
        query = query.filter(Match.resume_id == resume_id)
    if job_id is not None:
        query = query.filter(Match.job_id == job_id)
    if min_score is not None:
        query = query.filter(Match.overall_score >= min_score)
    if max_score is not None:
        query = query.filter(Match.overall_score <= max_score)
    total = query.count()
    items = [MatchBase.model_validate(item) for item in query.order_by(Match.overall_score.desc()).offset(skip).limit(limit)]
    return build_page(items=items, total=total, skip=skip, limit=limit)


@router.get("/{match_id}/explanation", response_model=MatchExplanationResponse)
def get_match_explanation(match_id: int, db: Session = Depends(get_db)) -> MatchExplanationResponse:
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return MatchExplanationResponse(match_id=match.id, explanation=match.explanation or {})


@router.get("/{match_id}", response_model=MatchBase)
def get_match(match_id: int, db: Session = Depends(get_db)) -> MatchBase:
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return MatchBase.model_validate(match)


@router.put("/{match_id}", response_model=MatchBase)
def update_match(match_id: int, payload: MatchUpdate, db: Session = Depends(get_db)) -> MatchBase:
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(match, field, value)
    db.commit()
    db.refresh(match)
    return MatchBase.model_validate(match)


@router.delete("/{match_id}")
def delete_match(match_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()
    return {"message": "Match deleted successfully"}
