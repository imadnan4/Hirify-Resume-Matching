from __future__ import annotations

from typing import Any

from app.services.text_processing import (
    dedupe_preserve_order,
    extract_degree_level,
    extract_required_years,
    extract_skill_candidates,
    keyword_overlap_score,
    most_common_tokens,
    normalize_whitespace,
)
from sqlalchemy.orm import Session

from app.models.job import JobDescription


def process_job_payload(title: str, description: str, requirements: str | None = None) -> dict[str, Any]:
    combined = normalize_whitespace("\n".join(part for part in [title, description, requirements or ""] if part))
    required_degree, required_degree_level = extract_degree_level(combined)
    required_years = extract_required_years(combined)
    skills = extract_skill_candidates(combined)
    return {
        "structured_data": {
            "normalized_text": combined,
            "required_degree": required_degree,
            "required_degree_level": required_degree_level,
            "required_years_experience": required_years,
            "top_keywords": most_common_tokens(combined, limit=15),
        },
        "extracted_skills": skills,
    }


def search_jobs_by_skills(db: Session, searched_skills: list[str], min_matches: int) -> list[dict]:
    results: list[dict] = []
    for job in db.query(JobDescription).yield_per(100):
        _, matched, _ = keyword_overlap_score(job.extracted_skills or [], searched_skills)
        if len(matched) >= min_matches:
            results.append(
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "skill_matches": len(matched),
                    "matched_skills": dedupe_preserve_order(matched),
                    "_score": len(matched),
                }
            )
    results.sort(key=lambda item: (-item["_score"], item["id"]))
    for result in results:
        result.pop("_score", None)
    return results
