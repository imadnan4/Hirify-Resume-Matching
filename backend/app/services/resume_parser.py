from __future__ import annotations

import re
from typing import Any

from app.schemas.resume import ResumePreviewResponse
from app.services.text_processing import (
    DATE_RANGE_RE,
    EMAIL_RE,
    PHONE_RE,
    URL_RE,
    dedupe_preserve_order,
    detect_sections,
    estimate_resume_years,
    extract_degree_level,
    extract_skill_candidates,
    normalize_token,
    normalize_whitespace,
    split_lines,
    split_skill_line,
)


def _pick_name(header_lines: list[str]) -> str | None:
    for line in header_lines[:5]:
        if "@" in line or any(char.isdigit() for char in line):
            continue
        words = line.strip().split()
        if 2 <= len(words) <= 4 and all(word[:1].isalpha() for word in words):
            return line.strip()
    return None


def _pick_location(header_lines: list[str]) -> str | None:
    for line in header_lines[:8]:
        if "@" in line or "http" in line.lower():
            continue
        if "," in line and len(line.split()) <= 8:
            return line.strip()
    return None


def _split_blocks(lines: list[str]) -> list[list[str]]:
    if not lines:
        return []
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if not line:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _parse_work_experience(lines: list[str]) -> list[dict[str, Any]]:
    blocks = _split_blocks(lines) or [lines] if lines else []
    items: list[dict[str, Any]] = []
    for block in blocks[:6]:
        joined = "\n".join(block)
        first = block[0] if block else ""
        second = block[1] if len(block) > 1 else ""
        date_match = DATE_RANGE_RE.search(joined)
        company = None
        job_title = first or None
        if " at " in first.lower():
            parts = re.split(r"\bat\b", first, maxsplit=1, flags=re.IGNORECASE)
            job_title = parts[0].strip() or None
            company = parts[1].strip() or None
        elif second and not date_match:
            company = second
        items.append(
            {
                "job_title": job_title,
                "company": company,
                "start_date": date_match.group("start") if date_match else None,
                "end_date": date_match.group("end") if date_match else None,
                "description": " ".join(block[1:]).strip() or None,
            }
        )
    return [item for item in items if any(item.values())]


def _parse_education(lines: list[str]) -> list[dict[str, Any]]:
    blocks = _split_blocks(lines) or [lines] if lines else []
    items: list[dict[str, Any]] = []
    for block in blocks[:4]:
        joined = " ".join(block)
        degree_name, _ = extract_degree_level(joined)
        year_match = re.search(r"(19|20)\d{2}", joined)
        institution = block[1] if len(block) > 1 else None
        items.append(
            {
                "degree": degree_name.title() if degree_name else block[0] if block else None,
                "field_of_study": None,
                "institution": institution,
                "graduation_year": int(year_match.group(0)) if year_match else None,
            }
        )
    return [item for item in items if any(item.values())]


def _extract_certifications(lines: list[str], text: str) -> list[str]:
    candidates: list[str] = []
    for line in lines:
        candidates.extend(part.strip() for part in re.split(r"[•,;|]+", line) if part.strip())
    for keyword in ("aws", "azure", "gcp", "scrum", "pmp", "ccna"):
        if keyword in text.lower():
            candidates.append(keyword)
    return dedupe_preserve_order(candidates)


def parse_resume_text(text: str) -> ResumePreviewResponse:
    normalized = normalize_whitespace(text)
    sections = detect_sections(text)
    header_lines = sections.get("header", [])[:10]
    summary_lines = sections.get("summary", [])
    work_lines = sections.get("work_experience", [])
    education_lines = sections.get("education", [])
    skill_lines = sections.get("skills", [])
    certification_lines = sections.get("certifications", [])

    email_match = EMAIL_RE.search(normalized)
    phone_match = PHONE_RE.search(normalized)
    urls = URL_RE.findall(normalized)

    summary = " ".join(summary_lines).strip() or None
    if not summary:
        paragraphs = [line for line in split_lines(normalized) if len(line.split()) > 8]
        summary = paragraphs[0] if paragraphs else None

    skills = []
    for line in skill_lines:
        skills.extend(split_skill_line(line))
    skills.extend(extract_skill_candidates(normalized))
    skills = dedupe_preserve_order(skills)

    preview = ResumePreviewResponse(
        contact_info={
            "full_name": _pick_name(header_lines),
            "email": email_match.group("email") if email_match else None,
            "phone": phone_match.group("phone").strip() if phone_match else None,
            "location": _pick_location(header_lines),
        },
        summary=summary,
        work_experience=_parse_work_experience(work_lines),
        education=_parse_education(education_lines),
        skills=skills,
        certifications=_extract_certifications(certification_lines, normalized),
        processing_metadata={
            "text_length": len(normalized),
            "detected_sections": sorted(sections.keys()),
            "urls_found": urls,
        },
    )
    return preview


def build_candidate_payload(preview: ResumePreviewResponse, source_text: str) -> dict[str, Any]:
    current_role = preview.work_experience[0] if preview.work_experience else None
    highest_education = preview.education[0] if preview.education else None
    return {
        "full_name": preview.contact_info.full_name,
        "email": preview.contact_info.email,
        "phone": preview.contact_info.phone,
        "location": preview.contact_info.location,
        "linkedin_url": next((url for url in preview.processing_metadata.get("urls_found", []) if "linkedin" in url.lower()), None),
        "portfolio_url": next(
            (
                url
                for url in preview.processing_metadata.get("urls_found", [])
                if "linkedin" not in url.lower()
            ),
            None,
        ),
        "years_experience": estimate_resume_years(source_text, [item.model_dump() for item in preview.work_experience]),
        "education_level": highest_education.degree if highest_education else None,
        "field_of_study": highest_education.field_of_study if highest_education else None,
        "university": highest_education.institution if highest_education else None,
        "graduation_year": highest_education.graduation_year if highest_education else None,
        "current_position": current_role.job_title if current_role else None,
        "current_company": current_role.company if current_role else None,
        "skills": preview.skills,
        "work_history": [item.model_dump() for item in preview.work_experience],
        "education_history": [item.model_dump() for item in preview.education],
        "certifications": preview.certifications,
        "languages": [],
        "projects": [],
        "achievements": [],
        "summary": preview.summary,
    }
