from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import auth, jobs, applications, profile
import os

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# Serve frontend SPA - catch-all for non-API routes
dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    index_path = os.path.join(dist_path, "index.html")
    file_path = os.path.join(dist_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"detail": "Not Found"}, status_code=404)
