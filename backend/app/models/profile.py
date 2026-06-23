from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class EntryCategory(str, enum.Enum):
    HONOR = "honor"
    QUALIFICATION = "qual"
    INTERNSHIP = "internship"
    CAMPUS = "campus"


class PersonalProfile(Base):
    __tablename__ = "personal_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(255))
    gender = Column(String(10))
    political_status = Column(String(50))
    contact1_name = Column(String(100))
    contact1_phone = Column(String(20))
    contact2_name = Column(String(100))
    contact2_phone = Column(String(20))
    home_address = Column(String(500))
    residence = Column(String(200))
    birthplace = Column(String(200))
    undergrad_school = Column(String(200))
    undergrad_college = Column(String(200))
    undergrad_period = Column(String(100))
    undergrad_major = Column(String(200))
    undergrad_gpa = Column(String(20))
    undergrad_gpa_rank = Column(String(50))
    undergrad_overall_score = Column(String(20))
    undergrad_overall_rank = Column(String(50))
    undergrad_transcript = Column(Text)
    grad_school = Column(String(200))
    grad_college = Column(String(200))
    grad_period = Column(String(100))
    grad_major = Column(String(200))
    grad_gpa = Column(String(20))
    grad_gpa_rank = Column(String(50))
    grad_overall_score = Column(String(20))
    grad_overall_rank = Column(String(50))
    grad_transcript = Column(Text)
    id_photo = Column(Text)
    location = Column(String(100))
    available_date = Column(String(100))
    education = Column(Text)
    certificates = Column(Text)
    experience = Column(Text)
    cover_letter_template = Column(Text)
    preferred_combinations = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    entries = relationship("ProfileEntry", back_populates="profile", cascade="all, delete-orphan")
    resume_files = relationship("ResumeFile", back_populates="profile", cascade="all, delete-orphan")


class ProfileEntry(Base):
    __tablename__ = "profile_entries"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("personal_profiles.id"), nullable=False)
    category = Column(SAEnum(EntryCategory), nullable=False, index=True)
    sort_order = Column(Integer, default=0)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    profile = relationship("PersonalProfile", back_populates="entries")
    files = relationship("ProfileEntryFile", back_populates="entry", cascade="all, delete-orphan")


class ProfileEntryFile(Base):
    __tablename__ = "profile_entry_files"
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("profile_entries.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(20))
    file_size = Column(Integer)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    entry = relationship("ProfileEntry", back_populates="files")


class ResumeFile(Base):
    __tablename__ = "resume_files"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("personal_profiles.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(20))
    file_size = Column(Integer)
    file_path = Column(String(500), nullable=False)
    category = Column(String(20), default="resume")
    created_at = Column(DateTime, server_default=func.now())
    profile = relationship("PersonalProfile", back_populates="resume_files")
