from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from service.Report_service import ReportService

router = APIRouter()

@router.get("/report/daily/{user_id}")
def get_daily_report(user_id: int, db: Session = Depends(get_db)):  # <-- Dipendenza DB
    return ReportService.get_daily_report(user_id, db)  # <-- Invocazione del service
