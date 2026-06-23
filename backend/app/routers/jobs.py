from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from typing import Optional
from datetime import date
from app.database import get_db
from app.models.job import JobPosting
from app.models.user import User
from app.schemas.job import JobPostingCreate, JobPostingResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["岗位"])

@router.get("/", response_model=dict)
def list_jobs(
    company: Optional[str] = Query(None), title: Optional[str] = Query(None),
    company_type: Optional[str] = Query(None), job_category: Optional[str] = Query(None),
    location: Optional[str] = Query(None), source: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None), keyword: Optional[str] = Query(None),
    deadline_before: Optional[date] = Query(None), deadline_after: Optional[date] = Query(None),
    sort_by: str = Query("created_at"), sort_order: str = Query("desc"),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    q = db.query(JobPosting)
    if company: q = q.filter(JobPosting.company.ilike(f"%{company}%"))
    if title: q = q.filter(JobPosting.title.ilike(f"%{title}%"))
    if company_type: q = q.filter(JobPosting.company_type == company_type)
    if job_category: q = q.filter(JobPosting.job_category == job_category)
    if location: q = q.filter(JobPosting.location.ilike(f"%{location}%"))
    if source: q = q.filter(JobPosting.source == source)
    if is_active is not None: q = q.filter(JobPosting.is_active == is_active)
    if keyword: q = q.filter(or_(JobPosting.company.ilike(f"%{keyword}%"), JobPosting.title.ilike(f"%{keyword}%"), JobPosting.description.ilike(f"%{keyword}%")))
    if deadline_before: q = q.filter(JobPosting.deadline <= deadline_before)
    if deadline_after: q = q.filter(JobPosting.deadline >= deadline_after)
    sort_col = getattr(JobPosting, sort_by, JobPosting.created_at)
    order_fn = desc if sort_order == "desc" else asc
    q = q.order_by(order_fn(sort_col))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": [JobPostingResponse.model_validate(j) for j in items]}

@router.get("/{job_id}", response_model=JobPostingResponse)
def get_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job: raise HTTPException(status_code=404, detail="岗位不存在")
    return JobPostingResponse.model_validate(job)

@router.post("/", response_model=JobPostingResponse)
def create_job(data: JobPostingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = JobPosting(**data.model_dump())
    db.add(job); db.commit(); db.refresh(job)
    return JobPostingResponse.model_validate(job)

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job: raise HTTPException(status_code=404, detail="岗位不存在")
    db.delete(job); db.commit()
    return {"ok": True}
