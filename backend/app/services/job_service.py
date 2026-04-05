from __future__ import annotations

from typing import Any

from app.services.text_processing import (
    extract_degree_level,
    extract_required_years,
    extract_skill_candidates,
    most_common_tokens,
    normalize_whitespace,
)


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
