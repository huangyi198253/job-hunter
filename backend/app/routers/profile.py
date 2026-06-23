from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os, uuid, json
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.profile import PersonalProfile, ProfileEntry, ProfileEntryFile, ResumeFile, EntryCategory
from app.schemas.profile import (
    PersonalProfileCreate, PersonalProfileResponse,
    ProfileEntryCreate, ProfileEntryUpdate, ProfileEntryResponse,
    EntryFileResponse, ResumeFileResponse,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["个人档案"])
PROFILE_DIR = "./uploads/profile"


def _build_response(profile):
    return PersonalProfileResponse(
        id=profile.id, user_id=profile.user_id,
        name=profile.name, phone=profile.phone, email=profile.email,
        gender=profile.gender, political_status=profile.political_status,
        contact1_name=profile.contact1_name, contact1_phone=profile.contact1_phone,
        contact2_name=profile.contact2_name, contact2_phone=profile.contact2_phone,
        home_address=profile.home_address, residence=profile.residence, birthplace=profile.birthplace,
        undergrad_school=profile.undergrad_school, undergrad_college=profile.undergrad_college,
        undergrad_period=profile.undergrad_period, undergrad_major=profile.undergrad_major,
        undergrad_gpa=profile.undergrad_gpa, undergrad_gpa_rank=profile.undergrad_gpa_rank,
        undergrad_overall_score=profile.undergrad_overall_score, undergrad_overall_rank=profile.undergrad_overall_rank,
        undergrad_transcript=json.loads(profile.undergrad_transcript) if profile.undergrad_transcript else None,
        grad_school=profile.grad_school, grad_college=profile.grad_college,
        grad_period=profile.grad_period, grad_major=profile.grad_major,
        grad_gpa=profile.grad_gpa, grad_gpa_rank=profile.grad_gpa_rank,
        grad_overall_score=profile.grad_overall_score, grad_overall_rank=profile.grad_overall_rank,
        grad_transcript=json.loads(profile.grad_transcript) if profile.grad_transcript else None,
        id_photo=json.loads(profile.id_photo) if profile.id_photo else None,
        location=profile.location, available_date=profile.available_date,
        cover_letter_template=profile.cover_letter_template,
        entries=[ProfileEntryResponse(
            id=e.id, category=e.category.value, sort_order=e.sort_order,
            data=json.loads(e.data) if isinstance(e.data, str) else e.data,
            files=[EntryFileResponse.model_validate(f) for f in (e.files or [])],
            created_at=e.created_at, updated_at=e.updated_at,
        ) for e in (profile.entries or [])],
        resume_files=[ResumeFileResponse.model_validate(f) for f in (profile.resume_files or [])],
        created_at=profile.created_at, updated_at=profile.updated_at,
    )


def _ensure_profile(user_id, db):
    p = db.query(PersonalProfile).filter(PersonalProfile.user_id == user_id).first()
    if not p:
        p = PersonalProfile(user_id=user_id)
        db.add(p); db.commit(); db.refresh(p)
    return p


@router.get("/", response_model=PersonalProfileResponse)
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _build_response(_ensure_profile(user.id, db))


@router.put("/", response_model=PersonalProfileResponse)
def update_profile(data: PersonalProfileCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _ensure_profile(user.id, db)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return _build_response(p)


# ----- Resume / Self-intro Files -----
@router.post("/resumes", response_model=ResumeFileResponse)
async def upload_resume(file: UploadFile = File(...), category: str = Form("resume"), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _ensure_profile(user.id, db)
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS: raise HTTPException(status_code=400, detail=f"不支持: .{ext}")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    uname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(PROFILE_DIR, uname)
    content = await file.read()
    with open(path, "wb") as f: f.write(content)
    rf = ResumeFile(profile_id=p.id, filename=uname, original_name=file.filename, file_type=ext, file_size=len(content), file_path=path, category=category)
    db.add(rf); db.commit(); db.refresh(rf)
    return ResumeFileResponse.model_validate(rf)


@router.get("/resumes", response_model=list[ResumeFileResponse])
def list_resumes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [ResumeFileResponse.model_validate(f) for f in _ensure_profile(user.id, db).resume_files]


@router.delete("/resumes/{file_id}")
def delete_resume(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(ResumeFile).join(PersonalProfile).filter(ResumeFile.id == file_id, PersonalProfile.user_id == user.id).first()
    if not f: raise HTTPException(status_code=404, detail="文件不存在")
    if os.path.exists(f.file_path): os.remove(f.file_path)
    db.delete(f); db.commit()
    return {"ok": True}


@router.put("/resumes/{file_id}/rename")
def rename_resume(file_id: int, name: str = Form(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    f = db.query(ResumeFile).join(PersonalProfile).filter(ResumeFile.id == file_id, PersonalProfile.user_id == user.id).first()
    if not f: raise HTTPException(status_code=404, detail="文件不存在")
    f.original_name = name
    db.commit()
    return {"ok": True}


# ----- Profile Entries -----
@router.get("/entries", response_model=list[ProfileEntryResponse])
def list_entries(category: str = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _ensure_profile(user.id, db)
    q = db.query(ProfileEntry).filter(ProfileEntry.profile_id == p.id)
    if category: q = q.filter(ProfileEntry.category == category)
    q = q.order_by(ProfileEntry.sort_order)
    return [ProfileEntryResponse(
        id=e.id, category=e.category.value, sort_order=e.sort_order,
        data=json.loads(e.data) if isinstance(e.data, str) else e.data,
        files=[EntryFileResponse.model_validate(f) for f in (e.files or [])],
        created_at=e.created_at, updated_at=e.updated_at,
    ) for e in q.all()]


@router.post("/entries", response_model=ProfileEntryResponse)
def create_entry(data: ProfileEntryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _ensure_profile(user.id, db)
    e = ProfileEntry(profile_id=p.id, category=data.category, sort_order=data.sort_order, data=json.dumps(data.data, ensure_ascii=False))
    db.add(e); db.commit(); db.refresh(e)
    return ProfileEntryResponse(id=e.id, category=e.category.value, sort_order=e.sort_order, data=json.loads(e.data), files=[], created_at=e.created_at, updated_at=e.updated_at)


@router.put("/entries/{entry_id}", response_model=ProfileEntryResponse)
def update_entry(entry_id: int, data: ProfileEntryUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.query(ProfileEntry).join(PersonalProfile).filter(ProfileEntry.id == entry_id, PersonalProfile.user_id == user.id).first()
    if not e: raise HTTPException(status_code=404, detail="条目不存在")
    if data.sort_order is not None: e.sort_order = data.sort_order
    if data.data is not None: e.data = json.dumps(data.data, ensure_ascii=False)
    db.commit(); db.refresh(e)
    return ProfileEntryResponse(id=e.id, category=e.category.value, sort_order=e.sort_order, data=json.loads(e.data),
        files=[EntryFileResponse.model_validate(f) for f in (e.files or [])], created_at=e.created_at, updated_at=e.updated_at)


@router.delete("/entries/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.query(ProfileEntry).join(PersonalProfile).filter(ProfileEntry.id == entry_id, PersonalProfile.user_id == user.id).first()
    if not e: raise HTTPException(status_code=404, detail="条目不存在")
    db.delete(e); db.commit()
    return {"ok": True}


# ----- Entry Files -----
@router.post("/entries/{entry_id}/files", response_model=EntryFileResponse)
async def upload_entry_file(entry_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    e = db.query(ProfileEntry).join(PersonalProfile).filter(ProfileEntry.id == entry_id, PersonalProfile.user_id == user.id).first()
    if not e: raise HTTPException(status_code=404, detail="条目不存在")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS: raise HTTPException(status_code=400, detail=f"不支持: .{ext}")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    uname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(PROFILE_DIR, uname)
    content = await file.read()
    with open(path, "wb") as f: f.write(content)
    pf = ProfileEntryFile(entry_id=entry_id, filename=uname, original_name=file.filename, file_type=ext, file_size=len(content), file_path=path)
    db.add(pf); db.commit(); db.refresh(pf)
    return EntryFileResponse.model_validate(pf)


@router.delete("/entries/files/{file_id}")
def delete_entry_file(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pf = db.query(ProfileEntryFile).join(ProfileEntry).join(PersonalProfile).filter(ProfileEntryFile.id == file_id, PersonalProfile.user_id == user.id).first()
    if not pf: raise HTTPException(status_code=404, detail="文件不存在")
    if os.path.exists(pf.file_path): os.remove(pf.file_path)
    db.delete(pf); db.commit()
    return {"ok": True}


# ----- Transcript / ID photo upload -----
@router.post("/transcript/{level}", response_model=PersonalProfileResponse)
async def upload_transcript(level: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _ensure_profile(user.id, db)
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS: raise HTTPException(status_code=400, detail=f"不支持: .{ext}")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    uname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(PROFILE_DIR, uname)
    content = await file.read()
    with open(path, "wb") as f: f.write(content)
    info = json.dumps({"filename": uname, "original_name": file.filename, "file_type": ext, "file_path": path}, ensure_ascii=False)
    if level == "undergrad": p.undergrad_transcript = info
    else: p.grad_transcript = info
    db.commit(); db.refresh(p)
    return _build_response(p)


@router.post("/idphoto", response_model=PersonalProfileResponse)
async def upload_id_photo(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = _ensure_profile(user.id, db)
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in {"png", "jpg", "jpeg", "gif", "webp"}: raise HTTPException(status_code=400, detail=f"不支持: .{ext}")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    uname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(PROFILE_DIR, uname)
    content = await file.read()
    with open(path, "wb") as f: f.write(content)
    p.id_photo = json.dumps({"filename": uname, "original_name": file.filename, "file_type": ext, "file_path": path}, ensure_ascii=False)
    db.commit(); db.refresh(p)
    return _build_response(p)
