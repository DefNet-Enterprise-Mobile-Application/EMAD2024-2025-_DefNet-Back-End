from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller import login_controller,registrazione_controller
from database.create_tables import create_database


app = FastAPI()

# Include the routers

# Login Routing 
app.include_router(login_controller.router)
# Registration Routing  
app.include_router(registrazione_controller.router)


# Inserisco la configurazione CORS per non avere eventuali blocchi al mio server locale 
# Preferibilmente è meglio settare l'indirizzo IP con porta locale 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Usa "*" per consentire tutte le origini (per scopi di sviluppo)
    allow_credentials=True,
    allow_methods=["*"],  # Consenti tutte le richieste HTTP
    allow_headers=["*"],
)


# Inizializza le tabelle al momento dell'avvio dell'applicazione
create_database()