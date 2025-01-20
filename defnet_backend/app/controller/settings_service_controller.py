import subprocess
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

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
async def toggle_service(service_name: str, service_request: ServiceRequest):
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

    # Risposta di successo
    return {"message": f"Service '{service_name}' has been {'enabled' if service_request.enabled else 'disabled'} successfully."}