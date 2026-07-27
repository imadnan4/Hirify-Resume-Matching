from __future__ import annotations

from sqlalchemy import cast, or_, String
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.resume import Resume
from app.schemas.resume import ResumePreviewResponse
from app.services.resume_parser import build_candidate_payload
from app.services.text_processing import dedupe_preserve_order, keyword_overlap_score


def upsert_candidate_from_resume(
    db: Session, *, resume: Resume, preview: ResumePreviewResponse, source_text: str
) -> Candidate:
    payload = build_candidate_payload(preview, source_text)
    candidate = resume.candidate
    if candidate is None:
        candidate = Candidate(resume_id=resume.id)
        db.add(candidate)
    for field, value in payload.items():
        setattr(candidate, field, value)
    return candidate


def search_candidates_by_skills(
    db: Session, searched_skills: list[str], min_matches: int, limit: int = 100
) -> list[dict]:
    # Database-level coarse filter: keep rows that contain at least one searched skill
    query = db.query(Candidate)
    if searched_skills:
        skill_filters = [
            cast(Candidate.skills, String).contains(skill)
            for skill in searched_skills
        ]
        query = query.filter(or_(*skill_filters))

    results: list[dict] = []
    for candidate in query.yield_per(100):
        score, matched, _ = keyword_overlap_score(candidate.skills or [], searched_skills)
        if len(matched) >= min_matches:
            results.append(
                {
                    "id": candidate.id,
                    "resume_id": candidate.resume_id,
                    "full_name": candidate.full_name,
                    "skill_matches": len(matched),
                    "matched_skills": dedupe_preserve_order(matched),
                    "_score": score,
                }
            )
    results.sort(key=lambda item: (-item["_score"], -item["skill_matches"], item["id"]))
    if limit:
        results = results[:limit]
    for result in results:
        result.pop("_score", None)
    return results
