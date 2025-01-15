from typing import Dict
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session
import logging
from service.user_service import get_user_by_id  # Importa la funzione per recuperare l'utente dal DB
from database.database import get_db  # Funzione per ottenere il DB dalla sessione

router = APIRouter()

# Configurazione logging per debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int, db: Session):
        """
        Aggiunge una nuova connessione dopo aver verificato l'user_id nel database.
        Se l'utente ha già una connessione, la chiude prima di accettarne una nuova.
        """
        logger.debug(f"Connessione WebSocket richiesta da {websocket.client.host}:{websocket.client.port}. User ID: {user_id}")
        
        try:
            user = get_user_by_id(db, user_id)
            logger.info(f"Connessione autorizzata per {user.username} con User ID: {user_id}.")
        except HTTPException as e:
            logger.error(f"Connessione rifiutata per user_id non valido: {e.detail}")
            await websocket.close(code=4000)
            return

        # Se esiste già una connessione per questo user_id, chiudi la connessione precedente
        if user_id in self.connections:
            logger.warning(f"Utente {user_id} ha già una connessione attiva, chiudendola...")
            current_ws = self.connections[user_id]
            if current_ws.client_state != WebSocketState.DISCONNECTED:
                await current_ws.close()  # Solo se non è già chiuso
            del self.connections[user_id]

        # Accettiamo la connessione solo se l'user_id è valido
        await websocket.accept()
        self.connections[user_id] = websocket
        logger.info(f"Connessione accettata per {user_id}")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Gestisce la disconnessione di un client.
        """
        try:
            if websocket.client_state == WebSocketState.DISCONNECTED:
                logger.warning(f"WebSocket già chiuso per User ID {user_id}. Non tentare di chiuderlo di nuovo.")
                return

            # Invia il messaggio di disconnessione
            await websocket.send_json({"action": "disconnect", "user_id": user_id})

            # Chiudi la connessione WebSocket
            await websocket.close()

            # Rimuovi la connessione dalla lista
            if user_id in self.connections:
                del self.connections[user_id]

            logger.info(f"WebSocket per User ID {user_id} chiuso con successo.")
        except Exception as e:
            logger.error(f"Errore durante la disconnessione del WebSocket per User ID {user_id}: {e}")

    async def broadcast(self, message: str):
        """
        Invia un messaggio a tutte le connessioni attive.
        """
        logger.debug(f"Broadcasting messaggio a {len(self.connections)} connessioni attive.")
        disconnected_clients = []
        for user_id, websocket in self.connections.items():
            try:
                await websocket.send_text(message)
                logger.info(f"Messaggio inviato a User ID {user_id}: {message}")
            except WebSocketDisconnect:
                disconnected_clients.append(user_id)
                logger.warning(f"Client con User ID {user_id} disconnesso durante il broadcast.")

        # Rimuovere i client disconnessi
        for user_id in disconnected_clients:
            del self.connections[user_id]
            logger.info(f"Rimosso client disconnesso con User ID: {user_id}")


# Istanza del gestore connessioni
manager = ConnectionManager()

@router.websocket("/ws/{user_id}/alerts")
async def websocket_alerts(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Connessione WebSocket iniziata per {websocket.client.host}:{websocket.client.port} con User ID: {user_id}")
    
    # Connessione WebSocket
    await manager.connect(websocket, user_id, db)
    
    # Invio della notifica di login appena l'utente si connette
    alert_message = f"Utente {user_id} ha effettuato il login"
    await manager.broadcast(f"Alert-System: {alert_message}")
    # Alert-system ---> relativo a messagistica di sistema ( Login , Cambio di valori e update ) ( verde )
    # Alert-info -----> relativo a attacchi non seri ( giallo )
    # Alert-Warning ----> relativo ad attacchi seri ( rosso )
    
    
    try:
        while True:
            data = await websocket.receive_json()
            # Gestisci i dati ricevuti...
    except WebSocketDisconnect:
        logger.info(f"Disconnessione WebSocket da {websocket.client.host}:{websocket.client.port}")
        await manager.disconnect(websocket=websocket, user_id=user_id)
    except Exception as e:
        logger.error(f"Errore durante la gestione del WebSocket: {e}")
        await websocket.close(code=4000)


@router.post("/ws/{user_id}/disconnect")
async def disconnect_user(user_id: int, db: Session = Depends(get_db)):
    """
    Disconnette un utente specifico utilizzando l'`user_id`.
    """
    logger.debug(f"Disconnessione WebSocket richiesta per User ID: {user_id}")

    # Verifica che l'utente esista nel database
    try:
        get_user_by_id(db, user_id)
    except HTTPException as e:
        logger.error(f"Impossibile disconnettere, user_id non valido: {e.detail}")
        raise HTTPException(status_code=400, detail="User ID non valido")

    # Verifica se il websocket per l'utente è connesso
    websocket = manager.connections.get(user_id)
    if websocket is None:
        logger.error(f"Nessuna connessione WebSocket trovata per User ID {user_id}")
        raise HTTPException(status_code=400, detail="Nessuna connessione WebSocket attiva")

    # Disconnessione dell'utente
    await manager.disconnect(websocket, user_id)
    return {"status": "success", "message": f"User {user_id} disconnected"}
