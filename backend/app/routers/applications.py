from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from typing import Optional, List
import os, uuid
from datetime import datetime, date
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.application import Application, ApplicationStatus, InterviewRound, InterviewType, ApplicationFile, ReviewNote
from app.schemas.application import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    InterviewRoundCreate, InterviewRoundResponse,
    ReviewNoteCreate, ReviewNoteResponse, FileResponse, ApplicationStats,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/applications", tags=["投递"])

def _app_to_response(app: Application) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id, user_id=app.user_id, job_id=app.job_id,
        company=app.company, title=app.title, location=app.location,
        company_type=app.company_type, job_category=app.job_category,
        status=app.status, next_step=app.next_step,
        next_reminder_at=app.next_reminder_at, notes=app.notes,
        applied_at=app.applied_at, created_at=app.created_at, updated_at=app.updated_at,
        interview_rounds=[InterviewRoundResponse.model_validate(r) for r in (app.interview_rounds or [])],
        files=[FileResponse.model_validate(f) for f in (app.files or [])],
        review_notes=[ReviewNoteResponse.model_validate(n) for n in (app.review_notes or [])],
    )

@router.get("/stats", response_model=ApplicationStats)
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Application).filter(Application.user_id == user.id)
    counts = {s.value: 0 for s in ApplicationStatus}
    for row in q.with_entities(Application.status, sa_func.count(Application.id)).group_by(Application.status).all():
        counts[row[0]] = row[1]
    today = date.today()
    t = q.filter(Application.next_reminder_at.isnot(None), sa_func.date(Application.next_reminder_at) == today).count()
    u = q.filter(Application.next_reminder_at.isnot(None), Application.next_reminder_at >= sa_func.now()).count()
    return ApplicationStats(
        total_saved=counts.get("收藏", 0), total_applied=counts.get("已投递", 0),
        total_written_test=counts.get("笔试", 0), total_interview=counts.get("面试", 0),
        total_offer=counts.get("Offer", 0), total_rejected=counts.get("拒信", 0),
        total_withdrawn=counts.get("放弃", 0), today_deadlines=t, upcoming_reminders=u,
    )

@router.get("/", response_model=dict)
def list_applications(status: Optional[str] = Query(None), company: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Application).filter(Application.user_id == user.id)
    if status: q = q.filter(Application.status == status)
    if company: q = q.filter(Application.company.ilike(f"%{company}%"))
    if keyword: q = q.filter(Application.company.ilike(f"%{keyword}%") | Application.title.ilike(f"%{keyword}%"))
    q = q.order_by(Application.updated_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": [_app_to_response(a) for a in items]}

@router.post("/", response_model=ApplicationResponse)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = Application(user_id=user.id, **data.model_dump())
    if data.status == ApplicationStatus.APPLIED: app.applied_at = datetime.now()
    db.add(app); db.commit(); db.refresh(app)
    return _app_to_response(app)

@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    return _app_to_response(app)

@router.put("/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, data: ApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(app, k, v)
    if data.status == ApplicationStatus.APPLIED and not app.applied_at: app.applied_at = datetime.now()
    db.commit(); db.refresh(app)
    return _app_to_response(app)

@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    db.delete(app); db.commit()
    return {"ok": True}

@router.post("/{app_id}/interviews", response_model=InterviewRoundResponse)
def add_interview_round(app_id: int, data: InterviewRoundCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    ir = InterviewRound(application_id=app_id, **data.model_dump())
    app.status = ApplicationStatus.INTERVIEW
    db.add(ir); db.commit(); db.refresh(ir)
    return InterviewRoundResponse.model_validate(ir)

@router.post("/{app_id}/files", response_model=FileResponse)
async def upload_file(app_id: int, file: UploadFile = File(...), tags: Optional[str] = Form(""),
    db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS: raise HTTPException(status_code=400, detail=f"不支持的文件类型: .{ext}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE: raise HTTPException(status_code=400, detail="文件过大")
    with open(file_path, "wb") as f: f.write(content)
    af = ApplicationFile(application_id=app_id, filename=unique_name, original_name=file.filename,
        file_type=ext, file_size=len(content), file_path=file_path, tags=tags)
    db.add(af); db.commit(); db.refresh(af)
    return FileResponse.model_validate(af)

@router.get("/{app_id}/files", response_model=List[FileResponse])
def list_files(app_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    return [FileResponse.model_validate(f) for f in app.files]

@router.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(ApplicationFile).join(Application).filter(ApplicationFile.id == file_id, Application.user_id == user.id).first()
    if not f: raise HTTPException(status_code=404, detail="文件不存在")
    if os.path.exists(f.file_path): os.remove(f.file_path)
    db.delete(f); db.commit()
    return {"ok": True}

@router.post("/{app_id}/reviews", response_model=ReviewNoteResponse)
def create_review(app_id: int, data: ReviewNoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    note = ReviewNote(application_id=app_id, **data.model_dump())
    db.add(note); db.commit(); db.refresh(note)
    return ReviewNoteResponse.model_validate(note)

@router.get("/{app_id}/reviews", response_model=List[ReviewNoteResponse])
def list_reviews(app_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not app: raise HTTPException(status_code=404, detail="投递记录不存在")
    return [ReviewNoteResponse.model_validate(n) for n in app.review_notes]
