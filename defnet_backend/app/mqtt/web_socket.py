from fastapi import WebSocket
from mqtt import mqtt_login
import asyncio
import json

# Lista dei client WebSocket connessi
websocket_clients = []

# Aggiungi un evento per la sincronizzazione
websocket_event = asyncio.Event()

async def add_websocket_client(websocket: WebSocket):
    """
    Aggiunge un client WebSocket alla lista dei client connessi.
    """
    print("Nuovo WebSocket connesso")
    await websocket.accept()
    websocket_clients.append(websocket)
    print(f"WebSocket aggiunto. Totale connessioni: {len(websocket_clients)}")  # Debug: numero totale di connessioni
    
    # Informa che almeno un WebSocket è connesso
    websocket_event.set()
    print("Evento websocket_event settato")
    
    # Invia l'ultimo messaggio del buffer
    if mqtt_login.message_buffer:
        last_message = mqtt_login.message_buffer[-1]
    #for message in mqtt_login.message_buffer:
        # Estrai solo la parte dopo "Message:"
        #if "Message:" in last_message:
            #message_content = last_message.split("type:")[1].strip()  # Ottieni solo la parte dopo "Message:"
        print(f"Inviando messaggio al WebSocket: {last_message}")  # Debug: invio messaggio
        await websocket.send_text(last_message)
    else:
        print("Nessun messaggio nel buffer da inviare.")

async def remove_websocket_client(websocket: WebSocket):
    """
    Rimuove un client WebSocket dalla lista dei client connessi.
    """
    websocket_clients.remove(websocket)

async def notify_websocket_clients(message: str):
    """
    Invia un messaggio a tutti i client WebSocket connessi.
    """
    
    print(f"Invio messaggio ai WebSocket: {message}")  # Debug: verifica l'esecuzione del metodo
    disconnected_clients = []
    
     # Controlla se ci sono WebSocket connessi
    if len(websocket_clients) == 0:
        print("Nessun WebSocket connesso, messaggio non inviato.")
        return
    
    for websocket in websocket_clients:
        try:
            print(f"Inviando messaggio al client WebSocket: {message}")  # Log per debugging
            await websocket.send_text(message)
            print(f"Messaggio inviato con successo al WebSocket: {websocket.client}")
        except Exception as e:
            print(f"Errore durante l'invio del messaggio al WebSocket: {e}")
            disconnected_clients.append(websocket)
            
    # Rimuove i WebSocket disconnessi dalla lista
    for websocket in disconnected_clients:
        websocket_clients.remove(websocket)
        print("WebSocket rimosso dalla lista dei client attivi")
