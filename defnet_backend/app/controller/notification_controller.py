

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from controller.websocket_controller import ConnectionManager

manager = ConnectionManager()


router = APIRouter()

@router.post("/notify-alert")
async def notify_alert(request: Request):
    """
    Endpoint per ricevere notifiche dal NotificationManager e inviarle ai WebSocket appropriati.
    """
    try:
        alert_data = await request.json()
        connection_type = alert_data.get("type", "alerts")  # Default "alerts"
        
        logging.info(f"Ricevuta notifica per {connection_type}: {alert_data}")
        await manager.broadcast(alert_data, connection_type=connection_type)
        
        return JSONResponse(status_code=200, content={"message": f"Notifica inoltrata ai client {connection_type}."})
    except Exception as e:
        logging.error(f"Errore nella gestione della notifica: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
