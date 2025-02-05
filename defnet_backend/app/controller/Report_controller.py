from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from service.Report_service import ReportService
from database.database import get_db
from fastapi.responses import JSONResponse
from datetime import datetime     
from random import choice

router = APIRouter()

# Endpoint per ottenere il report giornaliero
@router.get("/report/daily")
def get_daily_report(db: Session = Depends(get_db)):
    return ReportService.get_daily_report(db)  # <-- Invocazione del service

"""'
# Definisci i tipi di notifica
types = ['InfoSystem', 'AlertSystem', 'WarningSystem']

# Funzione per creare una notifica casuale
def create_notification(notification_type):
    return {
        'tipo': notification_type,
        'message': f"Questo è un messaggio di tipo {notification_type}",
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Crea 40 InfoSystem, 30 AlertSystem, 10 WarningSystem
info_system_notifications = [create_notification('InfoSystem') for _ in range(40)]
alert_system_notifications = [create_notification('AlertSystem') for _ in range(30)]
warning_system_notifications = [create_notification('WarningSystem') for _ in range(10)]

@router.get("/report/frontend")
def get_notifications():
    # Creazione delle notifiche come in precedenza
    all_notifications = info_system_notifications + alert_system_notifications + warning_system_notifications

    # Calcolare il conteggio delle notifiche per tipo
    notification_count = {
        'InfoSystem': sum(1 for n in all_notifications if n['tipo'] == 'InfoSystem'),
        'AlertSystem': sum(1 for n in all_notifications if n['tipo'] == 'AlertSystem'),
        'WarningSystem': sum(1 for n in all_notifications if n['tipo'] == 'WarningSystem'),
    }

    # Creare la risposta con il conteggio delle notifiche
    result = [
        {"tipo": key, "count": count}
        for key, count in notification_count.items()
    ]

    return JSONResponse(content={"notifiche": result})"""