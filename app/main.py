from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import Base
from app.routers import jobs, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobTracker API",
    description="Track job applications, interviews, and outcomes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
