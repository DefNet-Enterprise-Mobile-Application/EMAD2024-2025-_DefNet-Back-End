from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller import login_controller, registration_controller, profile_controller, logout_controller, speed_test_controller 


from database.create_tables import create_database

app = FastAPI()


# Include the routers

app.include_router(login_controller.router)
app.include_router(registration_controller.router)
app.include_router(profile_controller.router) 
app.include_router(logout_controller.router)
app.include_router(speed_test_controller.routes)

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
