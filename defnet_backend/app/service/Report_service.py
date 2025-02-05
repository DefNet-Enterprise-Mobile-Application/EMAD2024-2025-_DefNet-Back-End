from sqlalchemy import func
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.notification_alert import Notifica  
from datetime import datetime, timedelta

class ReportService:
    @staticmethod
    def get_daily_report(db: Session, date: datetime = None):
        try:
            if date is None:
                date = datetime.utcnow().date()  # Data di oggi

            # Filtra le notifiche che hanno timestamp_creazione nello stesso giorno
            daily_notifications = db.query(Notifica).filter(
                func.date(Notifica.timestamp_creazione) == date
            ).all()

            print(f"Notifiche per il {date}: {len(daily_notifications)} trovate.")

            # Conta il numero di notifiche per categoria
            notification_counts = {'system': 0, 'alert': 0, 'block': 0}
            for notification in daily_notifications:
                if notification.tipo == 'system':
                    notification_counts['system'] += 1
                elif notification.tipo == 'alert':
                    notification_counts['alert'] += 1
                elif notification.tipo == 'block':
                    notification_counts['block'] += 1

            return {
                "date": str(date),
                "notifiche": [
                    {"tipo": "system", "count": notification_counts['system']},
                    {"tipo": "alert", "count": notification_counts['alert']},
                    {"tipo": "block", "count": notification_counts['block']}
                ]
            }

        except Exception as e:
            print(f"Errore nella query giornaliera: {e}")
            raise HTTPException(status_code=500, detail="Errore nel recupero dei report giornalieri")

    @staticmethod
    def get_weekly_report(db: Session, date: datetime = None):
        try:
            if date is None:
                date = datetime.utcnow().date()  # Data di oggi
            
            start_date = date - timedelta(days=7)  # Settimana precedente
            
            # Filtra le notifiche negli ultimi 7 giorni
            weekly_notifications = db.query(Notifica).filter(
                func.date(Notifica.timestamp_creazione) >= start_date,
                func.date(Notifica.timestamp_creazione) <= date
            ).all()

            print(f"Notifiche tra {start_date} e {date}: {len(weekly_notifications)} trovate.")

            # Conta il numero di notifiche per categoria
            notification_counts = {'system': 0, 'alert': 0, 'block': 0}
            for notification in weekly_notifications:
                if notification.tipo == 'system':
                    notification_counts['system'] += 1
                elif notification.tipo == 'alert':
                    notification_counts['alert'] += 1
                elif notification.tipo == 'block':
                    notification_counts['block'] += 1

            return {
                "start_date": str(start_date),
                "end_date": str(date),
                "notifiche": [
                    {"tipo": "system", "count": notification_counts['system']},
                    {"tipo": "alert", "count": notification_counts['alert']},
                    {"tipo": "block", "count": notification_counts['block']}
                ]
            }

        except Exception as e:
            print(f"Errore nella query settimanale: {e}")
            raise HTTPException(status_code=500, detail="Errore nel recupero dei report settimanali")
