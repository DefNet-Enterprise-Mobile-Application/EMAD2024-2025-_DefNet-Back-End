from fastapi import FastAPI 
#from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware

from controller import login_controller, registration_controller, profile_controller
from controller import logout_controller, speed_test_controller ,notification_controller
from controller.websocket_controller import router as websocket_router 

from database.create_tables import create_database

#import asyncio

app = FastAPI()


# Include websocket route
app.include_router(websocket_router)


# Include the routers
app.include_router(login_controller.router)
app.include_router(registration_controller.router)
app.include_router(profile_controller.router) 
app.include_router(logout_controller.router)
app.include_router(speed_test_controller.router)
app.include_router(notification_controller.router)


# Configurazione CORS per il server locale
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Usa "*" per consentire tutte le origini (per scopi di sviluppo)
    allow_credentials=True,
    allow_methods=["*"],  # Consenti tutte le richieste HTTP
    allow_headers=["*"],
)


# Inizializza le tabelle al momento dell'avvio dell'applicazione
create_database()
