from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import time

from app.core.database import get_db
from app.schemas.match import (
    Match, MatchCreate, MatchList, BulkMatchRequest, 
    BulkMatchResponse, MatchExplanation, MatchStatistics, SingleMatchRequest
)
from app.services.matching_service import MatchingService
from app.services.resume_parser import ParsedResume, ContactInfo, WorkExperience, Education
from app.services.job_scraper import JobDescription
from app.models.resume import Resume as ResumeModel
from app.models.job_description import JobDescription as JobDescriptionModel  
from app.models.match import Match as MatchModel

router = APIRouter()

# Initialize matching service
matching_service = MatchingService()

@router.post("/match", response_model=dict)
async def match_resume_to_job_v2(
    request: SingleMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Match a specific resume to a specific job description using request body.
    
    - **resume_id**: ID of the resume to match
    - **job_id**: ID of the job description to match against
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
        if resume.status != "completed" or not resume.structured_data:
            raise HTTPException(status_code=400, detail="Resume not processed yet")
        
        # Convert database models to service models
        parsed_resume = convert_db_resume_to_parsed(resume)
        job_desc = convert_db_job_to_service(job)
        
        # Calculate match
        match_result = matching_service.calculate_match_score(parsed_resume, job_desc)
        
        # Save match to database
        db_match = MatchModel(
            resume_id=request.resume_id,
            job_id=request.job_id,
            overall_score=match_result.match_score.overall_score * 100,  # Convert to 0-100 scale
            skills_score=match_result.match_score.skills_score * 100,
            experience_score=match_result.match_score.experience_score * 100,
            education_score=match_result.match_score.education_score * 100,
            additional_score=match_result.match_score.additional_score * 100,
            matched_skills={"skills": match_result.matched_skills},
            missing_skills={"skills": match_result.missing_skills},
            skill_overlap_count=len(match_result.matched_skills),
            total_required_skills=len(match_result.matched_skills) + len(match_result.missing_skills),
            explanation={"explanation": match_result.match_score.explanation},
            confidence_level=_get_confidence_level(match_result.match_score.confidence),
            recommendation=_generate_recommendation(match_result.match_score.overall_score),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_match)
        db.commit()
        db.refresh(db_match)
        
        # Return detailed match result
        return {
            "match_id": db_match.id,
            "resume_id": request.resume_id,
            "job_id": request.job_id,
            "overall_score": match_result.match_score.overall_score,
            "score_breakdown": {
                "skills_score": match_result.match_score.skills_score,
                "experience_score": match_result.match_score.experience_score,
                "education_score": match_result.match_score.education_score,
                "additional_score": match_result.match_score.additional_score
            },
            "matched_skills": match_result.matched_skills,
            "missing_skills": match_result.missing_skills,
            "confidence": match_result.match_score.confidence,
            "explanation": match_result.match_score.explanation,
            "created_at": match_result.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")

@router.post("/match-body", response_model=dict)
async def match_resume_to_job_body(
    match_request: SingleMatchRequest,
    db: Session = Depends(get_db),
):
    """
    Match a single resume to a single job description using the request body.
    - **match_request**: Object containing resume_id and job_id
    """
    try:
        resume = db.query(ResumeModel).filter(ResumeModel.id == match_request.resume_id).first()
        job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == match_request.job_id).first()

        if not resume or not job:
            raise HTTPException(status_code=404, detail="Resume or Job not found")

        if resume.status != "completed" or not resume.structured_data:
            raise HTTPException(status_code=400, detail="Resume not processed yet")

        parsed_resume = convert_db_resume_to_parsed(resume)
        job_desc = convert_db_job_to_service(job)
        match_result = matching_service.calculate_match_score(parsed_resume, job_desc)

        return {
            "overall_score": match_result.match_score.overall_score,
            "skills_score": match_result.match_score.skills_score,
            "experience_score": match_result.match_score.experience_score,
            "education_score": match_result.match_score.education_score,
            "matched_skills": match_result.matched_skills,
            "missing_skills": match_result.missing_skills,
            "confidence": match_result.match_score.confidence,
            "explanation": match_result.match_score.explanation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

@router.post("/bulk-match", response_model=BulkMatchResponse)
async def bulk_match_resumes_to_jobs(
    match_request: BulkMatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Perform bulk matching of multiple resumes against multiple jobs.
    
    - **match_request**: Bulk matching request with resume IDs, job IDs, and options
    - Returns: Bulk matching results
    """
    try:
        start_time = time.time()
        
        # Validate input
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
        
        # Convert to service models
        parsed_resumes = [convert_db_resume_to_parsed(resume) for resume in resumes]
        job_descriptions = [convert_db_job_to_service(job) for job in jobs]
        
        # Perform bulk matching
        match_results = await matching_service.bulk_match(
            parsed_resumes,
            job_descriptions,
            match_request.min_score_threshold  # Already in 0-1 scale
        )
        
        # Save matches to database
        successful_matches = []
        failed_matches = []
        
        for match_result in match_results:
            try:
                # Find corresponding database IDs
                resume_id = next(r.id for r in resumes if str(hash(r.extracted_text[:100])) == match_result.resume_id)
                job_id = next(j.id for j in jobs if (j.id == int(match_result.job_id) if match_result.job_id.isdigit() else False))
                
                db_match = MatchModel(
                    resume_id=resume_id,
                    job_id=job_id,
                    overall_score=match_result.match_score.overall_score * 100,
                    skills_score=match_result.match_score.skills_score * 100,
                    experience_score=match_result.match_score.experience_score * 100,
                    education_score=match_result.match_score.education_score * 100,
                    additional_score=match_result.match_score.additional_score * 100,
                    matched_skills={"skills": match_result.matched_skills},
                    missing_skills={"skills": match_result.missing_skills},
                    skill_overlap_count=len(match_result.matched_skills),
                    total_required_skills=len(match_result.matched_skills) + len(match_result.missing_skills),
                    explanation={"explanation": match_result.match_score.explanation},
                    confidence_level=_get_confidence_level(match_result.match_score.confidence),
                    recommendation=_generate_recommendation(match_result.match_score.overall_score),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(db_match)
                db.commit()
                db.refresh(db_match)
                
                # Convert to API format (0.0-1.0 scale)
                match_dict = {
                    "id": db_match.id,
                    "resume_id": db_match.resume_id,
                    "job_id": db_match.job_id,
                    "overall_score": db_match.overall_score / 100.0,
                    "skills_score": db_match.skills_score / 100.0 if db_match.skills_score else None,
                    "experience_score": db_match.experience_score / 100.0 if db_match.experience_score else None,
                    "education_score": db_match.education_score / 100.0 if db_match.education_score else None,
                    "additional_score": db_match.additional_score / 100.0 if db_match.additional_score else None,
                    "matched_skills": db_match.matched_skills,
                    "missing_skills": db_match.missing_skills,
                    "skill_overlap_count": db_match.skill_overlap_count,
                    "total_required_skills": db_match.total_required_skills,
                    "explanation": db_match.explanation,
                    "confidence_level": db_match.confidence_level,
                    "recommendation": db_match.recommendation,
                    "created_at": db_match.created_at,
                    "updated_at": db_match.updated_at
                }
                successful_matches.append(Match.model_validate(match_dict))
                
            except Exception as e:
                failed_matches.append({
                    "resume_id": match_result.resume_id,
                    "job_id": match_result.job_id,
                    "error": str(e)
                })
        
        processing_time = time.time() - start_time
        
        return BulkMatchResponse(
            successful_matches=successful_matches,
            failed_matches=failed_matches,
            total_matches=len(successful_matches),
            processing_time=processing_time,
            summary={
                "total_resumes_processed": len(resumes),
                "total_jobs_processed": len(jobs),
                "matches_above_threshold": len(successful_matches),
                "average_processing_time": processing_time / len(match_results) if match_results else 0
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk matching failed: {str(e)}")

@router.get("/job/{job_id}/candidates", response_model=List[dict])
async def get_ranked_candidates_for_job(
    job_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get ranked candidates for a specific job.
    
    - **job_id**: ID of the job description
    - **limit**: Maximum number of candidates to return
    - Returns: List of ranked candidates
    """
    try:
        # Get all matches for this job
        matches = db.query(MatchModel).filter(
            MatchModel.job_id == job_id
        ).order_by(MatchModel.overall_score.desc()).limit(limit).all()
        
        if not matches:
            return []
        
        # Convert to service models for ranking
        service_matches = []
        for match in matches:
            # Create match result from database
            from app.services.matching_service import MatchResult, MatchScore
            
            match_score = MatchScore(
                overall_score=match.overall_score / 100.0,
                skills_score=match.skills_score / 100.0,
                experience_score=match.experience_score / 100.0,
                education_score=match.education_score / 100.0,
                additional_score=match.additional_score / 100.0,
                confidence=0.8,  # Default confidence
                explanation=match.explanation.get('explanation', '') if match.explanation else ''
            )
            
            match_result = MatchResult(
                resume_id=str(match.resume_id),
                job_id=str(match.job_id),
                match_score=match_score,
                matched_skills=match.matched_skills.get('skills', []) if match.matched_skills else [],
                missing_skills=match.missing_skills.get('skills', []) if match.missing_skills else [],
                created_at=match.created_at
            )
            
            service_matches.append(match_result)
        
        # Rank candidates
        ranked_candidates = matching_service.rank_candidates(service_matches, str(job_id))
        
        # Convert to response format
        result = []
        for candidate in ranked_candidates:
            # Get resume info
            resume = db.query(ResumeModel).filter(ResumeModel.id == int(candidate.resume_id)).first()
            
            result.append({
                "rank": candidate.rank,
                "percentile": candidate.percentile,
                "resume_id": candidate.resume_id,
                "candidate_name": resume.structured_data.get('contact_info', {}).get('full_name', 'Unknown') if resume.structured_data else 'Unknown',
                "overall_score": candidate.match_result.match_score.overall_score,
                "skills_score": candidate.match_result.match_score.skills_score,
                "experience_score": candidate.match_result.match_score.experience_score,
                "education_score": candidate.match_result.match_score.education_score,
                "matched_skills": candidate.match_result.matched_skills,
                "missing_skills": candidate.match_result.missing_skills,
                "explanation": candidate.match_result.match_score.explanation
            })
        
        return result
        
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
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **resume_id**: Filter by resume ID
    - **job_id**: Filter by job ID
    - **min_score**: Filter by minimum score
    - Returns: Paginated list of matches
    """
    query = db.query(MatchModel)
    
    # Apply filters
    if resume_id:
        query = query.filter(MatchModel.resume_id == resume_id)
    if job_id:
        query = query.filter(MatchModel.job_id == job_id)
    if min_score is not None:
        query = query.filter(MatchModel.overall_score >= min_score)
    
    total = query.count()
    matches = query.offset(skip).limit(limit).all()
    
    # Convert matches to API format (0.0-1.0 scale)
    api_matches = []
    for match in matches:
        match_dict = {
            "id": match.id,
            "resume_id": match.resume_id,
            "job_id": match.job_id,
            "overall_score": match.overall_score / 100.0,
            "skills_score": match.skills_score / 100.0 if match.skills_score else None,
            "experience_score": match.experience_score / 100.0 if match.experience_score else None,
            "education_score": match.education_score / 100.0 if match.education_score else None,
            "additional_score": match.additional_score / 100.0 if match.additional_score else None,
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "skill_overlap_count": match.skill_overlap_count,
            "total_required_skills": match.total_required_skills,
            "explanation": match.explanation,
            "confidence_level": match.confidence_level,
            "recommendation": match.recommendation,
            "created_at": match.created_at,
            "updated_at": match.updated_at
        }
        api_matches.append(Match.model_validate(match_dict))
    
    return MatchList(
        items=api_matches,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{match_id}", response_model=Match)
async def get_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific match by ID.
    
    - **match_id**: ID of the match
    - Returns: Match details
    """
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Convert to API format (0.0-1.0 scale)
    match_dict = {
        "id": match.id,
        "resume_id": match.resume_id,
        "job_id": match.job_id,
        "overall_score": match.overall_score / 100.0,
        "skills_score": match.skills_score / 100.0 if match.skills_score else None,
        "experience_score": match.experience_score / 100.0 if match.experience_score else None,
        "education_score": match.education_score / 100.0 if match.education_score else None,
        "additional_score": match.additional_score / 100.0 if match.additional_score else None,
        "matched_skills": match.matched_skills,
        "missing_skills": match.missing_skills,
        "skill_overlap_count": match.skill_overlap_count,
        "total_required_skills": match.total_required_skills,
        "explanation": match.explanation,
        "confidence_level": match.confidence_level,
        "recommendation": match.recommendation,
        "created_at": match.created_at,
        "updated_at": match.updated_at
    }
    
    return Match.model_validate(match_dict)

@router.get("/{match_id}/explanation", response_model=MatchExplanation)
async def get_match_explanation(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation for a match.
    
    - **match_id**: ID of the match
    - Returns: Detailed match explanation
    """
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Calculate skill overlap percentage
    matched_skills = match.matched_skills.get('skills', []) if match.matched_skills else []
    missing_skills = match.missing_skills.get('skills', []) if match.missing_skills else []
    total_skills = len(matched_skills) + len(missing_skills)
    skill_overlap_percentage = (len(matched_skills) / total_skills * 100) if total_skills > 0 else 0
    
    return MatchExplanation(
        overall_score=match.overall_score / 100.0,
        score_breakdown={
            "skills": match.skills_score / 100.0,
            "experience": match.experience_score / 100.0,
            "education": match.education_score / 100.0,
            "additional": match.additional_score / 100.0
        },
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        skill_overlap_percentage=skill_overlap_percentage,
        experience_match={"score": match.experience_score / 100.0},
        education_match={"score": match.education_score / 100.0},
        recommendations=_generate_detailed_recommendations(match)
    )

@router.delete("/{match_id}")
async def delete_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a match.
    
    - **match_id**: ID of the match to delete
    - Returns: Deletion confirmation
    """
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    db.delete(match)
    db.commit()
    
    return {"message": "Match deleted successfully"}

@router.get("/statistics/overview", response_model=MatchStatistics)
async def get_match_statistics(
    db: Session = Depends(get_db)
):
    """
    Get overall matching statistics.
    
    - Returns: Match statistics and trends
    """
    try:
        # Get all matches
        matches = db.query(MatchModel).all()
        
        if not matches:
            return MatchStatistics(
                total_matches=0,
                average_score=0.0,
                score_distribution={},
                top_matched_skills=[],
                match_trends={}
            )
        
        # Calculate statistics
        total_matches = len(matches)
        average_score = sum(match.overall_score for match in matches) / total_matches
        
        # Score distribution
        score_ranges = {
            "0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0
        }
        
        for match in matches:
            score = match.overall_score
            if score <= 20:
                score_ranges["0-20"] += 1
            elif score <= 40:
                score_ranges["21-40"] += 1
            elif score <= 60:
                score_ranges["41-60"] += 1
            elif score <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        
        # Top matched skills
        skill_counts = {}
        for match in matches:
            if match.matched_skills and 'skills' in match.matched_skills:
                for skill in match.matched_skills['skills']:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_skills = [
            {"skill": skill, "count": count}
            for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return MatchStatistics(
            total_matches=total_matches,
            average_score=average_score,
            score_distribution=score_ranges,
            top_matched_skills=top_skills,
            match_trends={"trend": "stable"}  # Placeholder
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics calculation failed: {str(e)}")

# Helper functions
def convert_db_resume_to_parsed(resume: ResumeModel) -> ParsedResume:
    """Convert database resume to ParsedResume service model"""
    if not resume.structured_data:
        raise ValueError("Resume not processed")
    
    data = resume.structured_data
    
    # Create contact info
    contact_info = ContactInfo(
        full_name=data.get('contact_info', {}).get('full_name', ''),
        email=data.get('contact_info', {}).get('email', ''),
        phone=data.get('contact_info', {}).get('phone', ''),
        address=data.get('contact_info', {}).get('location', '')
    )
    
    # Create work experience
    work_experience = []
    for exp_data in data.get('work_experience', []):
        work_exp = WorkExperience(
            title=exp_data.get('title', ''),
            company=exp_data.get('company', ''),
            location=exp_data.get('location', ''),
            start_date=exp_data.get('start_date', ''),
            end_date=exp_data.get('end_date', ''),
            description=exp_data.get('description', '')
        )
        work_experience.append(work_exp)
    
    # Create education
    education = []
    for edu_data in data.get('education', []):
        edu = Education(
            degree=edu_data.get('degree', ''),
            field_of_study=edu_data.get('field_of_study', ''),
            institution=edu_data.get('institution', ''),
            graduation_year=edu_data.get('graduation_year', '')
        )
        education.append(edu)
    
    return ParsedResume(
        contact_info=contact_info,
        work_experience=work_experience,
        education=education,
        skills=data.get('skills', {}),
        certifications=data.get('certifications', []),
        summary=data.get('summary', ''),
        raw_text=resume.extracted_text or '',
        processing_metadata=data.get('processing_metadata', {})
    )

def convert_db_job_to_service(job: JobDescriptionModel) -> JobDescription:
    """Convert database job to JobDescription service model"""
    skills = []
    if job.extracted_skills and 'skills' in job.extracted_skills:
        skills = job.extracted_skills['skills']
    
    return JobDescription(
        job_id=str(job.id),
        title=job.title,
        company=job.company,
        description=job.description,
        requirements=job.requirements or '',
        location=job.location,
        skills=skills,
        salary_range=job.salary_range,
        job_type=job.employment_type,  # Map employment_type to job_type
        experience_level=job.experience_level
    )

def _get_confidence_level(confidence: float) -> str:
    """Convert confidence score to level"""
    if confidence >= 0.8:
        return "high"
    elif confidence >= 0.6:
        return "medium"
    else:
        return "low"

def _generate_recommendation(score: float) -> str:
    """Generate recommendation based on score"""
    if score >= 0.8:
        return "Excellent match - highly recommended for consideration"
    elif score >= 0.6:
        return "Good match - recommended for review"
    elif score >= 0.4:
        return "Moderate match - may be suitable with additional evaluation"
    else:
        return "Low match - significant gaps in requirements"

def _generate_detailed_recommendations(match: MatchModel) -> List[str]:
    """Generate detailed recommendations for improvement"""
    recommendations = []
    
    if match.skills_score < 70:
        missing_skills = match.missing_skills.get('skills', []) if match.missing_skills else []
        if missing_skills:
            recommendations.append(f"Consider developing skills in: {', '.join(missing_skills[:3])}")
    
    if match.experience_score < 70:
        recommendations.append("Consider gaining more relevant experience in the field")
    
    if match.education_score < 70:
        recommendations.append("Consider pursuing additional education or certifications")
    
    return recommendations
