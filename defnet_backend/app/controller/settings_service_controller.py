import subprocess
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from requests import Session
from controller.websocket_controller import manager
from database.database import get_db


router = APIRouter()


# Modello per il corpo della richiesta
class ServiceRequest(BaseModel):
    service_name: str
    enabled: bool

# Simulazione di un database dei servizi
services_db: Dict[str, bool] = {
    "AD Block": True,
    "IDS and IPS": False,
    "Parental Control": False,
    "VPN Protection": False,
}


################################### IDS and IPS Service 


# Funzione per avviare IDS-IPS
def start_ids_ips():
    try:
        # Esegui il comando per avviare IDS-IPS
        subprocess.run(['/bin/ash', '/root/Defnet-IDS-IPS/openwrt-ids-ips-production.sh', 'start'], check=True)
        print("IDS-IPS started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting IDS-IPS: {e}")
        raise HTTPException(status_code=500, detail="Error starting IDS-IPS")



# TODO : Inserisci un oggetto per l'invio delle notifiche 
# TODO : Modifca la gestione della notifica 

# Funzione per fermare IDS-IPS
def stop_ids_ips():
    try:
        # Esegui il comando per fermare IDS-IPS
        subprocess.run(['/bin/ash', '/root/Defnet-IDS-IPS/openwrt-ids-ips-production.sh', 'stop'], check=True)
        print("IDS-IPS stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping IDS-IPS: {e}")
        raise HTTPException(status_code=500, detail="Error stopping IDS-IPS")







# Endpoint per attivare/disattivare i servizi
@router.put("/services/{service_name}")
async def toggle_service(service_name: str, service_request: ServiceRequest, db: Session = Depends(get_db)):
    # Verifica se il servizio esiste
    if service_name not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verifica che il nome del servizio nel corpo della richiesta corrisponda al nome del servizio nell'URL
    if service_name != service_request.service_name:
        raise HTTPException(status_code=400, detail="Service name mismatch")

    # Aggiorna lo stato del servizio nel "database"
    services_db[service_name] = service_request.enabled

    # Gestisci l'IDS-IPS separatamente
    if service_name == "IDS and IPS":
        if service_request.enabled:
            start_ids_ips()  # Avvia IDS-IPS
        else:
            stop_ids_ips()  # Ferma IDS-IPS


     # Prepara i dati di alert per il broadcast
    alert_data = {
        "serviceName": service_name,
        "newStatus": service_request.enabled,
        "description": f"Il servizio {service_name} è stato {'attivato' if service_request.enabled else 'disattivato'}.",
    }

    # Invia un messaggio di broadcast
    await manager.broadcast(alert_data, alert_type="serviceStatusChange", db=db)

    # Risposta di successo
    return {"message": f"Service '{service_name}' has been {'enabled' if service_request.enabled else 'disabled'} successfully."}



@router.get("/services", response_model=Dict[str, bool])
async def get_services_status():
    """
    Restituisce lo stato di tutti i servizi operativi.
    """
    try:
        return services_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero degli stati dei servizi: {e}")
