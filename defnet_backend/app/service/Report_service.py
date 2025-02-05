from sqlalchemy import func
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.notification_alert import Notifica  # Importa il modello Notifica
from datetime import datetime

class ReportService:
    @staticmethod
    def get_daily_report(db: Session):
        # Recupera tutte le notifiche dal database
        try:
            all_notifications = db.query(Notifica).all()
            
            # Stampa tutte le notifiche per debugging
            print("Tutte le notifiche nel database:")
            for notification in all_notifications:
                print(notification)

            # Aggiungi la logica di conteggio delle notifiche qui
            notification_counts = {
                'system': 0,
                'alert': 0,
                'block': 0
            }

            # Calcola il numero di notifiche per ogni tipo
            for notification in all_notifications:
                if notification.tipo == 'system':
                    notification_counts['system'] += 1
                elif notification.tipo == 'alert':
                    notification_counts['alert'] += 1
                elif notification.tipo == 'block':
                    notification_counts['block'] += 1

            return {
                "notifiche": [
                    {"tipo": "system", "count": notification_counts['system']},
                    {"tipo": "alert", "count": notification_counts['alert']},
                    {"tipo": "block", "count": notification_counts['block']}
                ]
            }

        except Exception as e:
            print(f"Errore nella query: {e}")
            raise