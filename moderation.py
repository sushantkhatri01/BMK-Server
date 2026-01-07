from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from server import get_db, User

router = APIRouter()

class ReportCreate(BaseModel):
    reporter_id: int
    reported_user_id: Optional[int] = None
    reported_message_id: Optional[int] = None
    reason: str
    details: Optional[str] = None

# In-memory store for reports (replace with DB in production)
REPORTS = []

@router.post("/report")
def report_content(report: ReportCreate, db: Session = Depends(get_db)):
    # In production, save to DB
    REPORTS.append(report.dict())
    return {"message": "Report submitted", "report": report.dict()}

@router.get("/reports")
def get_reports(admin: bool = False):
    # In production, restrict to admins
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return REPORTS
