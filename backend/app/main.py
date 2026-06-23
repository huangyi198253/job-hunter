from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import auth, jobs, applications, profile
import os

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(profile.router)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/health")
def health():
    return {"status": "ok", "version": settings.VERSION}
