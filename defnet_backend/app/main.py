from fastapi import FastAPI

from controller import login_controller 

from fastapi.middleware.cors import CORSMiddleware





app = FastAPI()

# Include the routers
app.include_router(login_controller.router)

# Inserisco la configurazione CORS per non avere eventuali blocchi al mio server locale 
# Preferibilmente è meglio settare l'indirizzo IP con porta locale 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Usa "*" per consentire tutte le origini (per scopi di sviluppo)
    allow_credentials=True,
    allow_methods=["*"],  # Consenti tutte le richieste HTTP
    allow_headers=["*"],
)