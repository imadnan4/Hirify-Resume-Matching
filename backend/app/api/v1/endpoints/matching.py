"""
Matching API Endpoints - Simplified for Semantic Matching
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import time

from app.core.database import get_db
from app.schemas.match import (
    Match, MatchCreate, MatchList, BulkMatchRequest, 
    BulkMatchResponse, MatchExplanation, MatchStatistics, SingleMatchRequest
)
from app.services.matching_engine import MatchingEngine, matching_engine
from app.services.resume_parser import ParsedResume, ContactInfo, WorkExperience, Education
from app.services.job_scraper import JobDescription
from app.models.resume import Resume as ResumeModel
from app.models.job_description import JobDescription as JobDescriptionModel  
from app.models.match import Match as MatchModel

router = APIRouter()


def _get_confidence_level(overall_score: float) -> str:
    """Convert overall score to confidence level tag"""
    if overall_score >= 0.7:
        return "high"
    elif overall_score >= 0.4:
        return "medium"
    return "low"


def _generate_recommendation(score: float) -> str:
    """Generate recommendation based on score"""
    if score >= 0.8:
        return "Excellent match - highly recommended for interview"
    elif score >= 0.6:
        return "Good match - consider for interview"
    elif score >= 0.4:
        return "Moderate match - review skills carefully"
    return "Low match - may not meet requirements"


@router.post("/match", response_model=dict)
async def match_resume_to_job(
    request: SingleMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Match a specific resume to a specific job description.
    
    - **resume_id**: ID of the resume
    - **job_id**: ID of the job description
    - Returns: Match result with detailed scoring
    """
    try:
        # Get resume and job from database
        resume = db.query(ResumeModel).filter(ResumeModel.id == request.resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Check if resume is processed
        if resume.status != "completed" or not resume.extracted_text:
            raise HTTPException(status_code=400, detail="Resume not processed yet")
        
        # Get text content
        resume_text = resume.extracted_text
        job_text = f"{job.title}\n{job.description}\n{job.requirements or ''}"
        
        # Calculate match using new engine
        match_result = matching_engine.match(resume_text, job_text)
        
        # Check if match already exists
        existing_match = db.query(MatchModel).filter(
            MatchModel.resume_id == request.resume_id,
            MatchModel.job_id == request.job_id
        ).first()
        
        if existing_match:
            # Update existing match (scores stored as 0-1)
            existing_match.overall_score = match_result.score.overall
            existing_match.skills_score = match_result.score.skills
            existing_match.experience_score = match_result.score.experience
            existing_match.education_score = match_result.score.education
            existing_match.additional_score = match_result.score.semantic
            existing_match.matched_skills = {"skills": match_result.matched_skills}
            existing_match.missing_skills = {"skills": match_result.missing_skills}
            existing_match.skill_overlap_count = len(match_result.matched_skills)
            existing_match.total_required_skills = len(match_result.matched_skills) + len(match_result.missing_skills)
            existing_match.explanation = {"explanation": match_result.explanation}
            existing_match.confidence_level = _get_confidence_level(match_result.score.overall)
            existing_match.recommendation = _generate_recommendation(match_result.score.overall)
            existing_match.updated_at = datetime.utcnow()
            db.commit()
            db_match = existing_match
        else:
            # Create new match (scores stored as 0-1)
            db_match = MatchModel(
                resume_id=request.resume_id,
                job_id=request.job_id,
                overall_score=match_result.score.overall,
                skills_score=match_result.score.skills,
                experience_score=match_result.score.experience,
                education_score=match_result.score.education,
                additional_score=match_result.score.semantic,
                matched_skills={"skills": match_result.matched_skills},
                missing_skills={"skills": match_result.missing_skills},
                skill_overlap_count=len(match_result.matched_skills),
                total_required_skills=len(match_result.matched_skills) + len(match_result.missing_skills),
                explanation={"explanation": match_result.explanation},
                confidence_level=_get_confidence_level(match_result.score.overall),
                recommendation=_generate_recommendation(match_result.score.overall),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_match)
            db.commit()
            db.refresh(db_match)
        
        return {
            "match_id": db_match.id,
            "overall_score": match_result.score.overall,
            "scores": {
                "semantic_similarity": match_result.score.semantic,
                "skills_match": match_result.score.skills,
                "experience_match": match_result.score.experience,
                "education_match": match_result.score.education
            },
            "matched_skills": match_result.matched_skills,
            "missing_skills": match_result.missing_skills,
            "skills_analysis": match_result.skill_details,
            "confidence": match_result.score.confidence,
            "explanation": match_result.explanation,
            "recommendation": _generate_recommendation(match_result.score.overall)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


@router.post("/bulk-match", response_model=dict)
async def bulk_match_resumes_to_jobs(
    match_request: BulkMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform bulk matching of multiple resumes against multiple jobs.
    """
    try:
        start_time = time.time()
        
        if not match_request.resume_ids or not match_request.job_ids:
            raise HTTPException(status_code=400, detail="Resume IDs and Job IDs are required")
        
        # Get resumes and jobs from database
        resumes = db.query(ResumeModel).filter(
            ResumeModel.id.in_(match_request.resume_ids),
            ResumeModel.status == "completed"
        ).all()
        
        jobs = db.query(JobDescriptionModel).filter(
            JobDescriptionModel.id.in_(match_request.job_ids)
        ).all()
        
        if not resumes:
            raise HTTPException(status_code=404, detail="No processed resumes found")
        if not jobs:
            raise HTTPException(status_code=404, detail="No job descriptions found")
        
        matches = []
        
        # Perform matching for each job-resume pair
        for job in jobs:
            job_text = f"{job.title}\n{job.description}\n{job.requirements or ''}"
            
            for resume in resumes:
                # Calculate match
                match_result = matching_engine.match(resume.extracted_text, job_text)
                
                if match_result.score.overall >= match_request.min_score_threshold:
                    # Check for existing match
                    existing = db.query(MatchModel).filter(
                        MatchModel.resume_id == resume.id,
                        MatchModel.job_id == job.id
                    ).first()
                    
                    if existing:
                        # Update existing (scores stored as 0-1)
                        existing.overall_score = match_result.score.overall
                        existing.skills_score = match_result.score.skills
                        existing.experience_score = match_result.score.experience
                        existing.education_score = match_result.score.education
                        existing.additional_score = match_result.score.semantic
                        existing.matched_skills = {"skills": match_result.matched_skills}
                        existing.missing_skills = {"skills": match_result.missing_skills}
                        existing.updated_at = datetime.utcnow()
                        db_match = existing
                    else:
                        # Save to database (scores stored as 0-1)
                        db_match = MatchModel(
                            resume_id=resume.id,
                            job_id=job.id,
                            overall_score=match_result.score.overall,
                            skills_score=match_result.score.skills,
                            experience_score=match_result.score.experience,
                            education_score=match_result.score.education,
                            additional_score=match_result.score.semantic,
                            matched_skills={"skills": match_result.matched_skills},
                            missing_skills={"skills": match_result.missing_skills},
                            skill_overlap_count=len(match_result.matched_skills),
                            total_required_skills=len(match_result.matched_skills) + len(match_result.missing_skills),
                            explanation={"explanation": match_result.explanation},
                            confidence_level=_get_confidence_level(match_result.score.overall),
                            recommendation=_generate_recommendation(match_result.score.overall),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(db_match)
                    
                    matches.append({
                        "resume_id": resume.id,
                        "job_id": job.id,
                        "overall_score": match_result.score.overall,
                        "matched_skills": match_result.matched_skills
                    })
        
        db.commit()
        
        processing_time = time.time() - start_time
        
        return {
            "total_matches": len(matches),
            "matches": matches,
            "processing_time_seconds": round(processing_time, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk matching failed: {str(e)}")


@router.get("/job/{job_id}/candidates")
async def get_ranked_candidates(
    job_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get ranked candidates for a specific job.
    """
    try:
        # Get all matches for this job
        matches = db.query(MatchModel).filter(
            MatchModel.job_id == job_id
        ).order_by(MatchModel.overall_score.desc()).limit(limit).all()
        
        if not matches:
            return []
        
        results = []
        for rank, match in enumerate(matches, 1):
            resume = db.query(ResumeModel).filter(ResumeModel.id == match.resume_id).first()
            
            candidate_name = "Unknown"
            if resume and resume.structured_data:
                contact_info = resume.structured_data.get('contact_info', {})
                candidate_name = contact_info.get('full_name', 'Unknown')
            
            results.append({
                "rank": rank,
                "resume_id": match.resume_id,
                "candidate_name": candidate_name,
                "overall_score": match.overall_score / 100.0,
                "skills_score": match.skills_score / 100.0,
                "experience_score": match.experience_score / 100.0,
                "matched_skills": match.matched_skills.get('skills', []) if match.matched_skills else [],
                "missing_skills": match.missing_skills.get('skills', []) if match.missing_skills else [],
                "recommendation": match.recommendation
            })
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")


@router.get("/", response_model=MatchList)
async def list_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resume_id: Optional[int] = Query(None),
    job_id: Optional[int] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    List all matches with pagination and filtering.
    """
    query = db.query(MatchModel)
    
    if resume_id:
        query = query.filter(MatchModel.resume_id == resume_id)
    if job_id:
        query = query.filter(MatchModel.job_id == job_id)
    if min_score:
        query = query.filter(MatchModel.overall_score >= min_score)
    
    total = query.count()
    matches = query.order_by(MatchModel.overall_score.desc()).offset(skip).limit(limit).all()
    
    # Calculate pagination info
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return MatchList(
        items=[Match.model_validate(m) for m in matches],
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/{match_id}", response_model=Match)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get a specific match by ID."""
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return Match.model_validate(match)


@router.delete("/{match_id}")
async def delete_match(match_id: int, db: Session = Depends(get_db)):
    """Delete a match."""
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()
    return {"status": "deleted", "id": match_id}


@router.get("/statistics/overview")
async def get_match_statistics(db: Session = Depends(get_db)):
    """Get overall matching statistics."""
    from sqlalchemy import func
    
    total_matches = db.query(MatchModel).count()
    
    if total_matches == 0:
        return {
            "total_matches": 0,
            "average_score": 0,
            "high_matches": 0,
            "medium_matches": 0,
            "low_matches": 0
        }
    
    avg_score = db.query(func.avg(MatchModel.overall_score)).scalar() or 0
    high_matches = db.query(MatchModel).filter(MatchModel.overall_score >= 80).count()
    medium_matches = db.query(MatchModel).filter(
        MatchModel.overall_score >= 50,
        MatchModel.overall_score < 80
    ).count()
    low_matches = db.query(MatchModel).filter(MatchModel.overall_score < 50).count()
    
    return {
        "total_matches": total_matches,
        "average_score": round(avg_score, 2),
        "high_matches": high_matches,
        "medium_matches": medium_matches,
        "low_matches": low_matches
    }
