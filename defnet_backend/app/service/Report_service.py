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
                print(f"ID: {notification.id}, Tipo: {notification.tipo}, Descrizione: {notification.descrizione}, "
                      f"Timestamp: {notification.timestamp}, Stato: {notification.stato}, User ID: {notification.user_id}")

            # Aggiungi la logica di conteggio delle notifiche qui
            notification_counts = {
                'InfoSystem': 0,
                'AlertSystem': 0,
                'WarningSystem': 0
            }

            # Calcola il numero di notifiche per ogni tipo
            for notification in all_notifications:
                if notification.tipo == 'InfoSystem':
                    notification_counts['InfoSystem'] += 1
                elif notification.tipo == 'AlertSystem':
                    notification_counts['AlertSystem'] += 1
                elif notification.tipo == 'WarningSystem':
                    notification_counts['WarningSystem'] += 1

            return {
                "notifiche": [
                    {"tipo": "InfoSystem", "count": notification_counts['InfoSystem']},
                    {"tipo": "AlertSystem", "count": notification_counts['AlertSystem']},
                    {"tipo": "WarningSystem", "count": notification_counts['WarningSystem']}
                ]
            }

        except Exception as e:
            print(f"Errore nella query: {e}")
            raise