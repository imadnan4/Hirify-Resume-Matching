from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .candidate import Candidate


class ResumeStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeBase(BaseModel):
    filename: str = Field(..., description="Original filename of the resume")
    file_type: Optional[str] = Field(None, description="File type (pdf, doc, docx)")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class ResumeCreate(ResumeBase):
    file_path: str = Field(..., description="Path to the uploaded file")


class ResumeUpdate(BaseModel):
    filename: Optional[str] = None
    status: Optional[ResumeStatus] = None
    processed_date: Optional[datetime] = None
    extracted_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    processing_errors: Optional[Dict[str, Any]] = None


class ResumeInDB(ResumeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    file_path: str
    upload_date: datetime
    processed_date: Optional[datetime] = None
    status: ResumeStatus
    extracted_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    processing_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Resume(ResumeInDB):
    """Resume schema for API responses"""
    pass


class ResumeWithCandidate(Resume):
    """Resume schema with candidate information"""
    candidate: Optional["Candidate"] = None


class ResumeList(BaseModel):
    """Schema for paginated resume list"""
    items: List[Resume]
    total: int
    page: int
    size: int
    pages: int


class ResumeUploadResponse(BaseModel):
    """Response schema for resume upload"""
    id: int
    filename: str
    file_size: int
    status: ResumeStatus
    upload_date: datetime
    message: str = "Resume uploaded successfully"


class ResumeProcessingStatus(BaseModel):
    """Schema for resume processing status"""
    id: int
    filename: str
    status: ResumeStatus
    processed_date: Optional[datetime] = None
    processing_errors: Optional[Dict[str, Any]] = None
    progress: Optional[float] = Field(None, description="Processing progress (0-100)")


class BulkResumeUpload(BaseModel):
    """Schema for bulk resume upload response"""
    successful: List[ResumeUploadResponse]
    failed: List[Dict[str, Any]]
    total_uploaded: int
    total_failed: int
