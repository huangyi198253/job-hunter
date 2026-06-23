from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, func
from app.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255))
    url = Column(Text)
    description = Column(Text)
    deadline = Column(Date, nullable=True)
    source = Column(String(100))
    source_url = Column(Text)
    company_type = Column(String(50), index=True)
    job_category = Column(String(50), index=True)
    is_active = Column(Boolean, default=True)
    last_seen_at = Column(DateTime, server_default=func.now())
    scraped_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
