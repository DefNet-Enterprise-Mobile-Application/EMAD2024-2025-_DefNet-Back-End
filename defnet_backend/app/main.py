from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from controller import login_controller, registration_controller, profile_controller, logout_controller, speed_test_controller 
from database.create_tables import create_database
from mqtt import mqtt_login, web_socket
import asyncio

app = FastAPI()

# Include the routers
app.include_router(login_controller.router)
app.include_router(registration_controller.router)
app.include_router(profile_controller.router) 
app.include_router(logout_controller.router)
app.include_router(speed_test_controller.router)

# Configurazione CORS per il server locale
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Usa "*" per consentire tutte le origini (per scopi di sviluppo)
    allow_credentials=True,
    allow_methods=["*"],  # Consenti tutte le richieste HTTP
    allow_headers=["*"],
)

async def heartbeat():
    """Task per verificare che il loop principale stia funzionando."""
    while True:
        print("Heartbeat: il loop è attivo.")
        await asyncio.sleep(10)
        
# Evento di startup per connettere MQTT
@app.on_event("startup")
async def startup_event():
    # Configura il loop principale
    
    try:
        loop = asyncio.get_running_loop()
      
        mqtt_login.set_main_event_loop(loop)

        # Connettiamo MQTT
        mqtt_login.connect_mqtt()
        
        # Sottoscrivi ai topic
        mqtt_login.subscribe_to_topics()
        
        # Configura il callback per i messaggi MQTT
        mqtt_login.mqtt_client.on_message = mqtt_login.mqtt_on_message  # Assegna la funzione di callback
    
        # Avvia il processo per leggere dalla coda e inviare i messaggi ai WebSocket
        asyncio.create_task(mqtt_login.process_message_queue())
    
        #asyncio.create_task(ensure_task(mqtt_login.process_message_queue))
        

    except Exception as e:
        print(f"Errore durante la configurazione MQTT: {e}")
        
    


# Evento di shutdown per disconnettere MQTT
@app.on_event("shutdown")
async def shutdown_event():
    # Disconnettiamo MQTT
    mqtt_login.disconnect_mqtt()
    


# WebSocket endpoint per notifiche
@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await web_socket.add_websocket_client(websocket)  # Usa la funzione del file separato
    try:
        while True:
            message = await websocket.receive_text()  # Mantieni la connessione attiva
            print(f"Messaggio ricevuto dal client WebSocket: {message}")  # Debug
    except Exception as e:
        await web_socket.remove_websocket_client(websocket)  # Rimuovi il client in caso di errore
        print(f"WebSocket disconnesso: {e}")
    
    

# Inizializza le tabelle al momento dell'avvio dell'applicazione
create_database()

async def ensure_task(coro_func):
    """Assicura che un task venga riavviato se fallisce."""
    while True:
        try:
            await coro_func()
        except Exception as e:
            print(f"Task terminato con errore: {e}. Riavvio del task...")
            await asyncio.sleep(1)  # Pausa breve prima di riavviare
