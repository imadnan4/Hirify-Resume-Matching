from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.candidate import Candidate, CandidateCreate, CandidateUpdate
from app.models.candidate import Candidate as CandidateModel
from app.models.resume import Resume as ResumeModel

router = APIRouter()

@router.get("/", response_model=List[Candidate])
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all candidates with pagination.
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - Returns: List of candidates
    """
    candidates = db.query(CandidateModel).offset(skip).limit(limit).all()
    return [Candidate.model_validate(candidate) for candidate in candidates]

@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific candidate by ID.
    
    - **candidate_id**: ID of the candidate
    - Returns: Candidate details
    """
    candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return Candidate.model_validate(candidate)

@router.get("/{candidate_id}/resume")
async def get_candidate_resume(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the resume associated with a candidate.
    
    - **candidate_id**: ID of the candidate
    - Returns: Resume information
    """
    candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.resume_id:
        raise HTTPException(status_code=404, detail="No resume associated with this candidate")
    
    resume = db.query(ResumeModel).filter(ResumeModel.id == candidate.resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "resume_id": resume.id,
        "resume_filename": resume.filename,
        "resume_status": resume.status,
        "processed_date": resume.processed_date,
        "structured_data": resume.structured_data
    }

@router.put("/{candidate_id}", response_model=Candidate)
async def update_candidate(
    candidate_id: int,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db)
):
    """
    Update candidate information.
    
    - **candidate_id**: ID of the candidate to update
    - **candidate_update**: Updated candidate data
    - Returns: Updated candidate
    """
    candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Update fields
    update_data = candidate_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    db.commit()
    db.refresh(candidate)
    
    return Candidate.model_validate(candidate)

@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a candidate.
    
    - **candidate_id**: ID of the candidate to delete
    - Returns: Deletion confirmation
    """
    candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    
    return {"message": "Candidate deleted successfully"}

@router.get("/search/by-skills")
async def search_candidates_by_skills(
    skills: str = Query(..., description="Comma-separated list of skills"),
    min_matches: int = Query(1, ge=1, description="Minimum number of skill matches"),
    db: Session = Depends(get_db)
):
    """
    Search candidates by skills.
    
    - **skills**: Comma-separated list of skills to search for
    - **min_matches**: Minimum number of skills that must match
    - Returns: Matching candidates
    """
    try:
        skill_list = [skill.strip().lower() for skill in skills.split(",")]
        
        # Get all candidates with resumes
        candidates = db.query(CandidateModel).filter(
            CandidateModel.resume_id.isnot(None)
        ).all()
        
        matching_candidates = []
        
        for candidate in candidates:
            resume = db.query(ResumeModel).filter(ResumeModel.id == candidate.resume_id).first()
            
            if resume and resume.structured_data and 'skills' in resume.structured_data:
                resume_skills = resume.structured_data['skills'].get('skills', [])
                if isinstance(resume_skills, list):
                    resume_skills_lower = [skill.get('skill', '').lower() for skill in resume_skills if isinstance(skill, dict)]
                    matches = len(set(skill_list) & set(resume_skills_lower))
                    
                    if matches >= min_matches:
                        candidate_dict = Candidate.model_validate(candidate).model_dump()
                        candidate_dict['skill_matches'] = matches
                        candidate_dict['matched_skills'] = list(set(skill_list) & set(resume_skills_lower))
                        matching_candidates.append(candidate_dict)
        
        # Sort by number of matches (descending)
        matching_candidates.sort(key=lambda x: x['skill_matches'], reverse=True)
        
        return {
            "candidates": matching_candidates,
            "total_matches": len(matching_candidates),
            "searched_skills": skill_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
