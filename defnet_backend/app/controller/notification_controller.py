import logging
from models.notification_alert import Notifica
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from controller.websocket_controller import manager
from database.database import SessionLocal, get_db  # Importa il tuo session manager per il DB

router = APIRouter()

@router.post("/notify-alert")
async def notify_alert(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint per ricevere notifiche dal NotificationManager e inviarle ai WebSocket appropriati.
    """
    try:
        alert_data = await request.json()
        print(f"Alert_Data : {alert_data}")

        events = alert_data.get("events", [])
        if not events:
            return JSONResponse(status_code=400, content={"error": "Nessun evento trovato nella notifica."})

        for event in events:
            alert_type = event.get("type", None)  # "alert" o "block"
            if not alert_type or alert_type not in ["alert", "block"]:
                logging.warning(f"Tipo di notifica non valido per l'evento: {event}")
                continue

            # Log della notifica ricevuta
            logging.info(f"Ricevuta notifica di tipo {alert_type}: {event}")

            # Richiama il metodo di broadcasting per ogni evento
            await manager.broadcast(event, alert_type, db)

        return JSONResponse(status_code=200, content={"message": f"{len(events)} notifiche elaborate correttamente."})
    except Exception as e:
        logging.error(f"Errore nella gestione della notifica: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})



# aggiornare lo stato di una notifica
@router.put("/notification_alert/{notification_id}/update-notification")
async def update_notification(notification_id: int, request: Request):
    """
    Endpoint per aggiornare lo stato di una notifica (lettura/not lettura).
    """
    try:
        print("Sto chiamando")
        # Ottieni i dati dalla richiesta
        data = await request.json()
        stato = data.get("stato")  # Stato che può essere True o False
        
        if stato is None:
            raise HTTPException(status_code=400, detail="Il parametro 'stato' è richiesto.")
        
        # Ottieni la sessione del database
        session: Session = SessionLocal()

        # Prova ad aggiornare lo stato tramite il metodo di classe
        notifica = Notifica.aggiorna_stato(session, notification_id, stato)

        if notifica is None:
            raise HTTPException(status_code=404, detail="Notifica non trovata.")

        logging.info(f"Notifica {notification_id} aggiornata con stato: {stato}")

        # Restituisci una risposta di successo
        return JSONResponse(
            status_code=200,
            content={"message": "Stato della notifica aggiornato con successo.", "notifica_id": notification_id},
        )

    except Exception as e:
        logging.error(f"Errore nell'aggiornamento della notifica: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
