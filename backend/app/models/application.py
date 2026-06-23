from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum, func
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ApplicationStatus(str, enum.Enum):
    SAVED = "收藏"
    APPLIED = "已投递"
    WRITTEN_TEST = "笔试"
    INTERVIEW = "面试"
    OFFER = "Offer"
    REJECTED = "拒信"
    WITHDRAWN = "放弃"

class InterviewType(str, enum.Enum):
    VIDEO = "视频面试"
    OFFLINE = "线下面试"
    PHONE = "电话面试"
    AI = "AI 面试"

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=True)
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255))
    company_type = Column(String(50))
    job_category = Column(String(50))
    status = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.SAVED, index=True)
    next_step = Column(String(255))
    next_reminder_at = Column(DateTime, nullable=True)
    notes = Column(Text)
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", backref="applications")
    job = relationship("JobPosting", backref="applications")
    interview_rounds = relationship("InterviewRound", back_populates="application", cascade="all, delete-orphan", order_by="InterviewRound.round_number")
    files = relationship("ApplicationFile", back_populates="application", cascade="all, delete-orphan")
    review_notes = relationship("ReviewNote", back_populates="application", cascade="all, delete-orphan", order_by="ReviewNote.created_at.desc()")

class InterviewRound(Base):
    __tablename__ = "interview_rounds"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    round_name = Column(String(100), default="")
    interview_type = Column(SAEnum(InterviewType), default=InterviewType.VIDEO)
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    application = relationship("Application", back_populates="interview_rounds")

class ApplicationFile(Base):
    __tablename__ = "application_files"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(20))
    file_size = Column(Integer)
    file_path = Column(String(500), nullable=False)
    tags = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    application = relationship("Application", back_populates="files")

class ReviewNote(Base):
    __tablename__ = "review_notes"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(500))
    ai_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    application = relationship("Application", back_populates="review_notes")
