from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.resume import Resume
from app.schemas.common import build_page
from app.schemas.resume import (
    BulkResumeFailure,
    BulkResumeUploadResponse,
    ResumeBase,
    ResumeListBase,
    ResumeListResponse,
    ResumePreviewResponse,
    ResumeStatusResponse,
    ResumeUpdate,
    ResumeUploadResponse,
)
from app.services.candidate_service import upsert_candidate_from_resume
from app.services.document_extractor import DocumentExtractor, UnsupportedDocumentTypeError
from app.services.embedding_service import cached_encode, get_embedding_provider
from app.services.resume_parser import build_candidate_payload, parse_resume_text

logger = logging.getLogger(__name__)
router = APIRouter()
extractor = DocumentExtractor()
embedder = get_embedding_provider()


def _validate_upload(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    suffix = Path(file.filename).suffix.lower()
    if suffix == ".doc":
        raise HTTPException(status_code=400, detail="Legacy .doc files are not supported in v1")
    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are allowed.")
    return suffix


async def _save_upload(file: UploadFile, suffix: str) -> tuple[Path, bytes]:
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    path = settings.resume_upload_dir / f"{uuid4()}{suffix}"
    path.write_bytes(content)
    return path, content


def _sync_candidate_metadata(preview: ResumePreviewResponse, text: str) -> ResumePreviewResponse:
    payload = build_candidate_payload(preview, text)
    preview.processing_metadata["estimated_years_experience"] = payload.get("years_experience")
    return preview


def _process_resume(db: Session, resume: Resume) -> ResumePreviewResponse:
    resume.status = "processing"
    resume.processing_errors = None
    db.commit()

    try:
        text = extractor.extract_text(resume.file_path)
        if not text.strip():
            raise ValueError("No readable text could be extracted from the document")

        preview = _sync_candidate_metadata(parse_resume_text(text), text)

        resume.extracted_text = text
        resume.structured_data = preview.model_dump()
        resume.embedding = cached_encode(embedder, text)
        resume.status = "completed"
        resume.processed_date = datetime.now(timezone.utc)
        resume.processing_errors = None
        upsert_candidate_from_resume(db, resume=resume, preview=preview, source_text=text)
        db.commit()
        db.refresh(resume)
        return preview
    except UnsupportedDocumentTypeError as exc:
        resume.status = "failed"
        resume.processing_errors = {"message": str(exc)}
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        resume.status = "failed"
        resume.processing_errors = {"message": str(exc)}
        db.commit()
        logger.exception("Resume processing failed for resume %s", resume.id)
        raise HTTPException(status_code=500, detail="Resume processing failed") from exc


@router.post("/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = _validate_upload(file)
    path, content = await _save_upload(file, suffix)
    resume = Resume(
        filename=file.filename or path.name,
        file_type=suffix.lstrip("."),
        file_size=len(content),
        file_path=str(path),
        status="pending",
    )
    try:
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception:
        db.rollback()
        if path.exists():
            path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to persist resume record")
    await asyncio.to_thread(_process_resume, db, resume)
    db.refresh(resume)
    return ResumeUploadResponse(
        id=resume.id,
        filename=resume.filename,
        file_size=resume.file_size,
        status=resume.status,
        upload_date=resume.upload_date,
    )


@router.post("/bulk-upload", response_model=BulkResumeUploadResponse, status_code=201)
async def bulk_upload_resumes(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    successful: list[ResumeUploadResponse] = []
    failed: list[BulkResumeFailure] = []
    for file in files:
        path: Path | None = None
        try:
            suffix = _validate_upload(file)
            path, content = await _save_upload(file, suffix)
            resume = Resume(
                filename=file.filename or path.name,
                file_type=suffix.lstrip("."),
                file_size=len(content),
                file_path=str(path),
                status="pending",
            )
            try:
                db.add(resume)
                db.commit()
                db.refresh(resume)
            except Exception:
                db.rollback()
                if path.exists():
                    path.unlink(missing_ok=True)
                raise
            await asyncio.to_thread(_process_resume, db, resume)
            db.refresh(resume)
            successful.append(
                ResumeUploadResponse(
                    id=resume.id,
                    filename=resume.filename,
                    file_size=resume.file_size,
                    status=resume.status,
                    upload_date=resume.upload_date,
                )
            )
        except HTTPException as exc:
            failed.append(BulkResumeFailure(filename=file.filename or "unknown", error=str(exc.detail)))
        except Exception as exc:
            failed.append(BulkResumeFailure(filename=file.filename or "unknown", error=str(exc)))
    return BulkResumeUploadResponse(
        successful=successful,
        failed=failed,
        total_uploaded=len(successful),
        total_failed=len(failed),
    )


@router.get("/", response_model=ResumeListResponse)
def list_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Resume)
    if status:
        query = query.filter(Resume.status == status)
    total = query.count()
    items = [ResumeListBase.model_validate(item) for item in query.order_by(Resume.id.desc()).offset(skip).limit(limit)]
    return build_page(items=items, total=total, skip=skip, limit=limit)


@router.get("/{resume_id}/status", response_model=ResumeStatusResponse)
def get_resume_status(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    progress_map = {"pending": 0, "processing": 50, "completed": 100, "failed": 0}
    return ResumeStatusResponse(
        id=resume.id,
        filename=resume.filename,
        status=resume.status,
        processed_date=resume.processed_date,
        processing_errors=resume.processing_errors,
        progress=progress_map.get(resume.status, 0),
    )


@router.get("/{resume_id}/preview", response_model=ResumePreviewResponse)
def preview_resume_data(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.structured_data:
        raise HTTPException(status_code=400, detail="Resume not processed or no data available")
    return ResumePreviewResponse.model_validate(resume.structured_data)


@router.post("/{resume_id}/reprocess")
def reprocess_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume.status = "pending"
    resume.processed_date = None
    resume.processing_errors = None
    resume.structured_data = None
    resume.extracted_text = None
    resume.embedding = None
    db.commit()
    _process_resume(db, resume)
    return {"message": "Resume reprocessing started"}


@router.get("/{resume_id}", response_model=ResumeBase)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return ResumeBase.model_validate(resume)


@router.put("/{resume_id}", response_model=ResumeBase)
def update_resume(resume_id: int, payload: ResumeUpdate, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(resume, field, value)
    db.commit()
    db.refresh(resume)
    return ResumeBase.model_validate(resume)


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    file_path = Path(resume.file_path)
    db.delete(resume)
    db.commit()
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass
    return {"message": "Resume deleted successfully"}
