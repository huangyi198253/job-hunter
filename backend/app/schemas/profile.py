from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class EntryFileResponse(BaseModel):
    id: int; filename: str; original_name: str
    file_type: Optional[str] = None; file_size: Optional[int] = None; created_at: datetime
    model_config = {"from_attributes": True}


class ProfileEntryResponse(BaseModel):
    id: int; category: str; sort_order: int; data: Any
    files: List[EntryFileResponse] = []
    created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class ProfileEntryCreate(BaseModel):
    category: str; sort_order: int = 0; data: Any


class ProfileEntryUpdate(BaseModel):
    sort_order: Optional[int] = None; data: Optional[Any] = None


class ResumeFileResponse(BaseModel):
    id: int; filename: str; original_name: str
    file_type: Optional[str] = None; file_size: Optional[int] = None
    category: str; created_at: datetime
    model_config = {"from_attributes": True}


class PersonalProfileCreate(BaseModel):
    name: Optional[str] = None; phone: Optional[str] = None; email: Optional[str] = None
    gender: Optional[str] = None; political_status: Optional[str] = None
    contact1_name: Optional[str] = None; contact1_phone: Optional[str] = None
    contact2_name: Optional[str] = None; contact2_phone: Optional[str] = None
    home_address: Optional[str] = None; residence: Optional[str] = None; birthplace: Optional[str] = None
    undergrad_school: Optional[str] = None; undergrad_college: Optional[str] = None
    undergrad_period: Optional[str] = None; undergrad_major: Optional[str] = None
    undergrad_gpa: Optional[str] = None; undergrad_gpa_rank: Optional[str] = None
    undergrad_overall_score: Optional[str] = None; undergrad_overall_rank: Optional[str] = None
    grad_school: Optional[str] = None; grad_college: Optional[str] = None
    grad_period: Optional[str] = None; grad_major: Optional[str] = None
    grad_gpa: Optional[str] = None; grad_gpa_rank: Optional[str] = None
    grad_overall_score: Optional[str] = None; grad_overall_rank: Optional[str] = None


class PersonalProfileResponse(BaseModel):
    id: int; user_id: int
    name: Optional[str] = None; phone: Optional[str] = None; email: Optional[str] = None
    gender: Optional[str] = None; political_status: Optional[str] = None
    contact1_name: Optional[str] = None; contact1_phone: Optional[str] = None
    contact2_name: Optional[str] = None; contact2_phone: Optional[str] = None
    home_address: Optional[str] = None; residence: Optional[str] = None; birthplace: Optional[str] = None
    undergrad_school: Optional[str] = None; undergrad_college: Optional[str] = None
    undergrad_period: Optional[str] = None; undergrad_major: Optional[str] = None
    undergrad_gpa: Optional[str] = None; undergrad_gpa_rank: Optional[str] = None
    undergrad_overall_score: Optional[str] = None; undergrad_overall_rank: Optional[str] = None
    undergrad_transcript: Optional[Any] = None
    grad_school: Optional[str] = None; grad_college: Optional[str] = None
    grad_period: Optional[str] = None; grad_major: Optional[str] = None
    grad_gpa: Optional[str] = None; grad_gpa_rank: Optional[str] = None
    grad_overall_score: Optional[str] = None; grad_overall_rank: Optional[str] = None
    grad_transcript: Optional[Any] = None
    id_photo: Optional[Any] = None
    location: Optional[str] = None; available_date: Optional[str] = None
    cover_letter_template: Optional[str] = None
    entries: List[ProfileEntryResponse] = []
    resume_files: List[ResumeFileResponse] = []
    created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}
