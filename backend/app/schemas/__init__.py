from .resume import (
    Resume,
    ResumeCreate,
    ResumeUpdate,
    ResumeInDB,
    ResumeList,
    ResumeUploadResponse,
    ResumeProcessingStatus,
    BulkResumeUpload,
    ResumeWithCandidate,
    ResumeStatus,
)

from .job_description import (
    JobDescription,
    JobDescriptionCreate,
    JobDescriptionUpdate,
    JobDescriptionInDB,
    JobDescriptionList,
    BulkJobDescriptionCreate,
)

from .candidate import (
    Candidate,
    CandidateCreate,
    CandidateUpdate,
    CandidateInDB,
    CandidateList,
    CandidateScore,
    CandidateScoreCreate,
)

from .match import (
    Match,
    MatchCreate,
    MatchUpdate,
    MatchInDB,
    MatchList,
    MatchWithDetails,
    BulkMatchRequest,
    BulkMatchResponse,
    MatchExplanation,
    MatchHistory,
    MatchHistoryCreate,
    MatchStatistics,
)

__all__ = [
    # Resume schemas
    "Resume",
    "ResumeCreate",
    "ResumeUpdate",
    "ResumeInDB",
    "ResumeList",
    "ResumeUploadResponse",
    "ResumeProcessingStatus",
    "BulkResumeUpload",
    "ResumeWithCandidate",
    "ResumeStatus",
    
    # Job Description schemas
    "JobDescription",
    "JobDescriptionCreate",
    "JobDescriptionUpdate",
    "JobDescriptionInDB",
    "JobDescriptionList",
    "BulkJobDescriptionCreate",
    
    # Candidate schemas
    "Candidate",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateInDB",
    "CandidateList",
    "CandidateScore",
    "CandidateScoreCreate",
    
    # Match schemas
    "Match",
    "MatchCreate",
    "MatchUpdate",
    "MatchInDB",
    "MatchList",
    "MatchWithDetails",
    "BulkMatchRequest",
    "BulkMatchResponse",
    "MatchExplanation",
    "MatchHistory",
    "MatchHistoryCreate",
    "MatchStatistics",
]

# Pydantic schemas package