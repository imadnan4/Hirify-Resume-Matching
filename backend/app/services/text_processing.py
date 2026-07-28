from __future__ import annotations

import re
from collections import Counter
from typing import Iterable


SECTION_ALIASES = {
    "summary": {"summary", "professional summary", "profile", "about"},
    "work_experience": {"experience", "work experience", "employment history", "professional experience"},
    "education": {"education", "academic background", "academics"},
    "skills": {"skills", "technical skills", "core skills", "competencies"},
    "certifications": {"certifications", "licenses", "certificates"},
    "projects": {"projects"},
}

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "nodejs": "node.js",
    "node": "node.js",
    "postgresql": "postgres",
    "py": "python",
    "aws certified cloud practitioner": "aws",
}

SKILL_VOCABULARY = {
    "aws",
    "azure",
    "gcp",
    "react",
    "next.js",
    "vue",
    "angular",
    "typescript",
    "javascript",
    "node.js",
    "express",
    "python",
    "django",
    "flask",
    "fastapi",
    "java",
    "spring",
    "kotlin",
    "go",
    "rust",
    "c++",
    "c#",
    ".net",
    "sql",
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "docker",
    "kubernetes",
    "terraform",
    "graphql",
    "rest",
    "html",
    "css",
    "tailwind",
    "figma",
    "git",
    "github actions",
    "ci/cd",
    "linux",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "nlp",
    "llm",
    "rag",
    "prompt engineering",
}

DEGREE_LEVELS = {
    "high school": 1,
    "diploma": 1,
    "associate": 2,
    "bachelor": 3,
    "bs": 3,
    "ba": 3,
    "bsc": 3,
    "master": 4,
    "ms": 4,
    "msc": 4,
    "ma": 4,
    "mba": 4,
    "phd": 5,
    "doctorate": 5,
}

EMAIL_RE = re.compile(r"(?P<email>[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.IGNORECASE)
PHONE_RE = re.compile(r"(?P<phone>(?:\+?\d[\d()\-\s]{7,}\d))")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
YEARS_RE = re.compile(r"(?P<years>\d{1,2})\+?\s+(?:years|yrs)", re.IGNORECASE)
_MONTH_RE = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_RANGE_RE = re.compile(
    rf"(?P<start>(?:{_MONTH_RE}\.?\s*\d{4}|\d{4}))\s*(?:-|\u2013|to)\s*(?P<end>present|current|now|(?:{_MONTH_RE}\.?\s*\d{4}|\d{4}))",
    re.IGNORECASE,
)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).replace("\r\n", "\n").replace("\r", "\n").strip()


def normalize_token(value: str) -> str:
    token = value.strip().lower()
    token = re.sub(r"\s+", " ", token)
    return SKILL_ALIASES.get(token, token)


def split_lines(text: str) -> list[str]:
    return [line.strip() for line in normalize_whitespace(text).split("\n") if line.strip()]


def detect_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower().rstrip(":")
        matched_section = next(
            (name for name, aliases in SECTION_ALIASES.items() if lowered in aliases),
            None,
        )
        if matched_section:
            current = matched_section
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def tokenize_for_matching(text: str) -> list[str]:
    cleaned = normalize_whitespace(text).lower()
    return re.findall(r"[a-z0-9.+#/-]+", cleaned)


def extract_skill_candidates(text: str) -> list[str]:
    lowered = f" {normalize_whitespace(text).lower()} "
    found: list[str] = []
    for skill in sorted(SKILL_VOCABULARY, key=len, reverse=True):
        pattern = rf"(?<![a-z0-9]){re.escape(skill.lower())}(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.append(skill)
    return dedupe_preserve_order(found)


def split_skill_line(line: str) -> list[str]:
    chunks = re.split(r"[|,/•·;]+", line)
    return [normalize_token(chunk) for chunk in chunks if normalize_token(chunk)]


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_token(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def extract_degree_level(text: str | None) -> tuple[str | None, int]:
    if not text:
        return None, 0
    lowered = normalize_whitespace(text).lower()
    best_name = None
    best_level = 0
    for degree, level in DEGREE_LEVELS.items():
        if degree in lowered and level > best_level:
            best_name = degree
            best_level = level
    return best_name, best_level


def extract_required_years(text: str | None) -> int | None:
    if not text:
        return None
    matches = [int(match.group("years")) for match in YEARS_RE.finditer(text)]
    return max(matches) if matches else None


def estimate_resume_years(text: str, work_experience: list[dict] | None = None) -> int | None:
    if work_experience:
        inferred = []
        for item in work_experience:
            source = " ".join(
                str(item.get(key) or "") for key in ("start_date", "end_date", "description")
            )
            years = extract_required_years(source)
            if years:
                inferred.append(years)
        if inferred:
            return max(inferred)

    matches = [int(match.group("years")) for match in YEARS_RE.finditer(text)]
    if matches:
        return max(matches)

    date_ranges = list(DATE_RANGE_RE.finditer(text))
    if date_ranges:
        return min(max(len(date_ranges) * 2, 1), 30)
    return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    numerator = sum(x * y for x, y in zip(a, b))
    denom_a = sum(x * x for x in a) ** 0.5
    denom_b = sum(y * y for y in b) ** 0.5
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return max(0.0, min(1.0, numerator / (denom_a * denom_b)))


def keyword_overlap_score(left: Iterable[str], right: Iterable[str]) -> tuple[float, list[str], list[str]]:
    left_set = {normalize_token(item) for item in left if normalize_token(item)}
    right_set = {normalize_token(item) for item in right if normalize_token(item)}
    if not right_set:
        return 0.0, [], []
    matched = sorted(left_set & right_set)
    missing = sorted(right_set - left_set)
    return len(matched) / max(len(right_set), 1), matched, missing


def most_common_tokens(text: str, limit: int = 12) -> list[str]:
    tokens = [token for token in tokenize_for_matching(text) if len(token) > 2]
    counts = Counter(tokens)
    return [token for token, _ in counts.most_common(limit)]
