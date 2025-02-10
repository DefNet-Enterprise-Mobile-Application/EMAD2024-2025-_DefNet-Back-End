from typing import Dict
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session
import logging
import asyncio

from service.user_service import get_user_by_id  # Importa la funzione per recuperare l'utente dal DB
from database.database import get_db  # Funzione per ottenere il DB dalla sessione
from models.notification_alert import Notifica



router = APIRouter()

# Configurazione logging per debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

    async def broadcast(self, alert_data: dict, alert_type: str, db: Session):
        """
        Salva la notifica nel database e invia un messaggio a tutte le connessioni attive.
        """
        try:
            # Salva la notifica nel database
            nuova_notifica = Notifica.salva_notifica(
                session=db,
                tipo=alert_type,
                descrizione=alert_data.get("description", "Nessuna descrizione fornita.")
            )
            formatted_timestamp = nuova_notifica.timestamp_creazione.strftime('%d %B %Y, %H:%M')

            # Prepara il messaggio da inviare
            notification_message = {
                "id": nuova_notifica.id,
                "tipo": nuova_notifica.tipo,
                "descrizione": nuova_notifica.descrizione,
                "timestamp": formatted_timestamp,
                "stato": nuova_notifica.stato  # False = non letta
            }


            # Aggiungi i dati del servizio, se presenti
            if alert_type == "service-changed":
                notification_message.update({
                    "serviceName": alert_data.get("serviceName", "Unknown"),
                    "newStatus": alert_data.get("newStatus", False),
                })

            # Invia la notifica a tutte le connessioni attive
            disconnected_clients = []
            for user_id, websocket in self.connections.items():
                try:
                    if websocket.client_state != WebSocketState.DISCONNECTED:
                        await websocket.send_json(notification_message)
                        logger.info(f"Notifica inviata a User ID {user_id}: {notification_message}")
                    else:
                        disconnected_clients.append(user_id)
                except WebSocketDisconnect:
                    disconnected_clients.append(user_id)
                    logger.warning(f"Client con User ID {user_id} disconnesso durante il broadcast.")

            # Rimuovere i client disconnessi
            for user_id in disconnected_clients:
                del self.connections[user_id]
                logger.info(f"Rimosso client disconnesso con User ID: {user_id}")
        except Exception as e:
            logger.error(f"Errore durante il broadcast: {e}")


    async def send_heartbeat(self,websocket: WebSocket):
        while True:
            try:
                await websocket.send_json({"action": "ping"})
            except Exception as e:
                logger.error("Errore inviando il ping: %s", e)
                break
            await asyncio.sleep(30)  # invia un ping ogni 30 secondi


    async def send_message_to_user(self, user_id: int, message: str, db: Session):
        """
        Invia un messaggio solo al WebSocket di un determinato utente.
        """
        
        if user_id in self.connections:
            websocket = self.connections[user_id]
            if websocket.client_state != WebSocketState.DISCONNECTED:
                # Salva la notifica nel database
                nuova_notifica = Notifica.salva_notifica(session=db, tipo="system", descrizione=message, user_id=user_id)
                 # Formatta il timestamp come giorno e ora
                formatted_timestamp = nuova_notifica.timestamp_creazione.strftime('%d %B %Y, %H:%M')
                print(f"Nuova notifica creata: {nuova_notifica}")
                # Invia la notifica al frontend come JSON
                await websocket.send_json({
                    "id": nuova_notifica.id,
                    "tipo": nuova_notifica.tipo,
                    "descrizione": nuova_notifica.descrizione,
                    "timestamp": formatted_timestamp,
                    "stato": nuova_notifica.stato,  # False = non letta
                    "user_id": nuova_notifica.user_id
                })
                logger.info(f"Messaggio inviato a User ID {user_id}: {message}")
            else:
                logger.warning(f"WebSocket già disconnesso per User ID {user_id}. Messaggio non inviato.")
        else:
            logger.warning(f"Nessuna connessione trovata per User ID {user_id}.")




# Istanza del gestore connessioni
manager = ConnectionManager()

@router.websocket("/ws/{user_id}/notifications")
async def websocket_alerts(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Connessione WebSocket iniziata per {websocket.client.host}:{websocket.client.port} con User ID: {user_id}")
    
    # Connessione WebSocket
    await manager.connect(websocket, user_id, db)
    
    # Invio della notifica di login appena l'utente si connette
    alert_message = f"Utente {user_id} ha effettuato il login"
    await manager.send_message_to_user(user_id, alert_message, db=db)
    
    # Avvia il task per il heartbeat (invio periodico del ping)
    heartbeat_task = asyncio.create_task(manager.send_heartbeat(websocket))
    
    try:
        while True:
            data = await websocket.receive_json()
            # Se riceviamo un "pong", significa che il client ha risposto al ping
            if data.get("action") == "pong":
                logger.debug(f"Ricevuto pong da User ID {user_id}")
                continue  # Puoi aggiornare uno stato o un timestamp qui, se necessario
            # Gestisci altri tipi di messaggi
            logger.debug(f"Messaggio ricevuto da User ID {user_id}: {data}")
    except WebSocketDisconnect:
        logger.info(f"Disconnessione WebSocket da {websocket.client.host}:{websocket.client.port}")
        await manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"Errore durante la gestione del WebSocket: {e}")
        await websocket.close(code=4000)
    finally:
        heartbeat_task.cancel()  # Cancella il task del ping quando la connessione termina





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
