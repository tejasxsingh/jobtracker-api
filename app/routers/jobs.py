from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models import JobApplication, ApplicationStatus, User
from app.schemas import JobCreate, JobUpdate, JobResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_job = JobApplication(**job.model_dump(), owner_id=user.id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    status: Optional[ApplicationStatus] = None,
    company: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(JobApplication).filter(JobApplication.owner_id == user.id)

    if status:
        query = query.filter(JobApplication.status == status)
    if company:
        query = query.filter(JobApplication.company.ilike(f"%{company}%"))

    query = query.order_by(JobApplication.last_updated.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """quick breakdown of application counts by status"""
    apps = db.query(JobApplication).filter(JobApplication.owner_id == user.id).all()

    counts = {}
    for s in ApplicationStatus:
        counts[s.value] = sum(1 for a in apps if a.status == s)

    return {"total": len(apps), "by_status": counts}


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(JobApplication).filter(
        JobApplication.id == job_id, JobApplication.owner_id == user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="application not found")
    return job


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int, updates: JobUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    job = db.query(JobApplication).filter(
        JobApplication.id == job_id, JobApplication.owner_id == user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="application not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(JobApplication).filter(
        JobApplication.id == job_id, JobApplication.owner_id == user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="application not found")

    db.delete(job)
    db.commit()
