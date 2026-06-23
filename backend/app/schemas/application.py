from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.application import ApplicationStatus, InterviewType

class InterviewRoundCreate(BaseModel):
    round_number: int; round_name: str = ""
    interview_type: InterviewType = InterviewType.VIDEO
    interview_date: Optional[datetime] = None; notes: Optional[str] = None

class InterviewRoundResponse(BaseModel):
    id: int; application_id: int; round_number: int; round_name: str
    interview_type: InterviewType; interview_date: Optional[datetime] = None
    notes: Optional[str] = None; created_at: datetime
    model_config = {"from_attributes": True}

class ApplicationCreate(BaseModel):
    job_id: Optional[int] = None; company: str; title: str
    location: Optional[str] = None; company_type: Optional[str] = None
    job_category: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    next_step: Optional[str] = None; next_reminder_at: Optional[datetime] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None; next_step: Optional[str] = None
    next_reminder_at: Optional[datetime] = None; notes: Optional[str] = None

class FileResponse(BaseModel):
    id: int; filename: str; original_name: str; file_type: Optional[str] = None
    file_size: Optional[int] = None; tags: Optional[str] = None; created_at: datetime
    model_config = {"from_attributes": True}

class ReviewNoteResponse(BaseModel):
    id: int; content: str; tags: Optional[str] = None
    ai_analysis: Optional[str] = None; created_at: datetime
    model_config = {"from_attributes": True}

class ReviewNoteCreate(BaseModel):
    content: str; tags: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int; user_id: int; job_id: Optional[int] = None
    company: str; title: str; location: Optional[str] = None
    company_type: Optional[str] = None; job_category: Optional[str] = None
    status: ApplicationStatus; next_step: Optional[str] = None
    next_reminder_at: Optional[datetime] = None; notes: Optional[str] = None
    applied_at: Optional[datetime] = None; created_at: datetime; updated_at: datetime
    interview_rounds: List[InterviewRoundResponse] = []
    files: List[FileResponse] = []
    review_notes: List[ReviewNoteResponse] = []
    model_config = {"from_attributes": True}

class ApplicationStats(BaseModel):
    total_saved: int = 0; total_applied: int = 0; total_written_test: int = 0
    total_interview: int = 0; total_offer: int = 0; total_rejected: int = 0
    total_withdrawn: int = 0; today_deadlines: int = 0; upcoming_reminders: int = 0
