from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.schemas.resume import ResumePreviewResponse
from app.services.embedding_service import cached_encode, get_embedding_provider
from app.services.text_processing import (
    cosine_similarity,
    dedupe_preserve_order,
    extract_degree_level,
    extract_required_years,
    extract_skill_candidates,
    keyword_overlap_score,
    normalize_token,
)


@dataclass
class MatchComputation:
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    additional_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    skill_overlap_count: int
    total_required_skills: int
    confidence_level: str
    recommendation: str
    explanation: dict[str, Any]
    resume_embedding: list[float]
    job_embedding: list[float]


class MatchingService:
    def __init__(self) -> None:
        self.embedder = get_embedding_provider()

    def compute_match(
        self,
        *,
        resume_text: str,
        resume_preview: ResumePreviewResponse,
        job_title: str,
        job_description: str,
        job_requirements: str | None,
        job_skills: list[str] | None,
        job_structured_data: dict[str, Any] | None,
    ) -> MatchComputation:
        job_text = "\n".join(part for part in [job_title, job_description, job_requirements or ""] if part)
        resume_embedding = cached_encode(self.embedder, resume_text)
        job_embedding = cached_encode(self.embedder, job_text)
        semantic_similarity = cosine_similarity(resume_embedding, job_embedding)

        resume_skills = dedupe_preserve_order(resume_preview.skills + extract_skill_candidates(resume_text))
        required_skills = dedupe_preserve_order((job_skills or []) + extract_skill_candidates(job_text))
        overlap_ratio, matched_skills, missing_skills = keyword_overlap_score(resume_skills, required_skills)
        skills_score = round((semantic_similarity * 0.45) + (overlap_ratio * 0.55), 4)

        experience_score = self._score_experience(
            resume_text=resume_text,
            resume_preview=resume_preview,
            job_text=job_text,
            semantic_similarity=semantic_similarity,
            job_structured_data=job_structured_data,
        )
        education_score = self._score_education(
            resume_preview=resume_preview,
            job_text=job_text,
            semantic_similarity=semantic_similarity,
            job_structured_data=job_structured_data,
        )
        additional_score = self._score_additional(
            resume_text=resume_text,
            resume_preview=resume_preview,
            job_text=job_text,
            matched_skills=matched_skills,
            semantic_similarity=semantic_similarity,
        )

        overall_score = round(
            (skills_score * settings.match_weight_skills)
            + (experience_score * settings.match_weight_experience)
            + (education_score * settings.match_weight_education)
            + (additional_score * settings.match_weight_additional),
            4,
        )
        overall_score = max(0.0, min(1.0, overall_score))

        confidence_level = self._confidence_level(
            overall_score=overall_score,
            matched_skills=matched_skills,
            semantic_similarity=semantic_similarity,
            preview=resume_preview,
        )
        recommendation = self._recommendation(overall_score)
        explanation = {
            "score_breakdown": {
                "semantic_similarity": round(semantic_similarity, 4),
                "skills_score": skills_score,
                "experience_score": experience_score,
                "education_score": education_score,
                "additional_score": additional_score,
                "overall_score": overall_score,
            },
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "reasons": self._reasons(
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                experience_score=experience_score,
                education_score=education_score,
                additional_score=additional_score,
            ),
        }
        return MatchComputation(
            overall_score=overall_score,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            additional_score=additional_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            skill_overlap_count=len(matched_skills),
            total_required_skills=len(required_skills),
            confidence_level=confidence_level,
            recommendation=recommendation,
            explanation=explanation,
            resume_embedding=resume_embedding,
            job_embedding=job_embedding,
        )

    def _score_experience(
        self,
        *,
        resume_text: str,
        resume_preview: ResumePreviewResponse,
        job_text: str,
        semantic_similarity: float,
        job_structured_data: dict[str, Any] | None,
    ) -> float:
        required_years = None
        if job_structured_data:
            required_years = job_structured_data.get("required_years_experience")
        if required_years is None:
            required_years = extract_required_years(job_text)

        candidate_years = None
        if resume_preview.processing_metadata:
            candidate_years = resume_preview.processing_metadata.get("estimated_years_experience")
        if candidate_years is None:
            from app.services.text_processing import estimate_resume_years

            candidate_years = estimate_resume_years(resume_text)

        if required_years and candidate_years:
            ratio = min(candidate_years / max(required_years, 1), 1.0)
            return round((ratio * 0.7) + (semantic_similarity * 0.3), 4)
        if resume_preview.work_experience:
            return round((semantic_similarity * 0.6) + 0.4, 4)
        return round(semantic_similarity * 0.6, 4)

    def _score_education(
        self,
        *,
        resume_preview: ResumePreviewResponse,
        job_text: str,
        semantic_similarity: float,
        job_structured_data: dict[str, Any] | None,
    ) -> float:
        required_level = 0
        if job_structured_data:
            required_level = int(job_structured_data.get("required_degree_level") or 0)
        if not required_level:
            _, required_level = extract_degree_level(job_text)

        candidate_text = " ".join(
            filter(
                None,
                [
                    item.degree or ""
                    for item in resume_preview.education
                ],
            )
        )
        _, candidate_level = extract_degree_level(candidate_text)
        if required_level and candidate_level:
            ratio = min(candidate_level / required_level, 1.0)
            return round((ratio * 0.75) + (semantic_similarity * 0.25), 4)
        if resume_preview.education:
            return round((semantic_similarity * 0.5) + 0.35, 4)
        return round(semantic_similarity * 0.4, 4)

    def _score_additional(
        self,
        *,
        resume_text: str,
        resume_preview: ResumePreviewResponse,
        job_text: str,
        matched_skills: list[str],
        semantic_similarity: float,
    ) -> float:
        cert_bonus = 0.1 if resume_preview.certifications else 0.0
        keyword_bonus = min(len(matched_skills) / 10, 0.25)
        location_bonus = 0.05 if "remote" in job_text.lower() else 0.0
        summary_bonus = 0.1 if resume_preview.summary else 0.0
        return round(min(semantic_similarity * 0.5 + cert_bonus + keyword_bonus + location_bonus + summary_bonus, 1.0), 4)

    def _confidence_level(
        self,
        *,
        overall_score: float,
        matched_skills: list[str],
        semantic_similarity: float,
        preview: ResumePreviewResponse,
    ) -> str:
        evidence_count = int(bool(preview.summary)) + len(preview.work_experience) + len(preview.education)
        if overall_score >= 0.75 and semantic_similarity >= 0.65 and (matched_skills or evidence_count >= 2):
            return "high"
        if overall_score >= 0.45:
            return "medium"
        return "low"

    def _recommendation(self, overall_score: float) -> str:
        if overall_score >= 0.8:
            return "Excellent match - highly recommended for interview"
        if overall_score >= 0.65:
            return "Good match - consider for interview"
        if overall_score >= 0.45:
            return "Moderate match - review skills carefully"
        return "Low match - may not meet requirements"

    def _reasons(
        self,
        *,
        matched_skills: list[str],
        missing_skills: list[str],
        experience_score: float,
        education_score: float,
        additional_score: float,
    ) -> list[str]:
        reasons: list[str] = []
        if matched_skills:
            reasons.append(f"Matched skills: {', '.join(matched_skills[:6])}")
        if missing_skills:
            reasons.append(f"Missing skills: {', '.join(missing_skills[:6])}")
        if experience_score >= 0.65:
            reasons.append("Experience profile aligns well with the role")
        elif experience_score < 0.4:
            reasons.append("Experience evidence is weaker than the role expects")
        if education_score >= 0.65:
            reasons.append("Education requirements appear to be met")
        if additional_score >= 0.6:
            reasons.append("Supporting factors like certifications or summary improve the fit")
        return reasons


matching_service = MatchingService()
