from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class JobPostingBase(BaseModel):
    company: str; title: str; location: Optional[str] = None
    url: Optional[str] = None; description: Optional[str] = None
    deadline: Optional[date] = None; source: Optional[str] = None
    source_url: Optional[str] = None; company_type: Optional[str] = None
    job_category: Optional[str] = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingResponse(JobPostingBase):
    id: int; is_active: bool
    last_seen_at: Optional[datetime] = None; scraped_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}
