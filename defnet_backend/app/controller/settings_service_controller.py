import subprocess
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
from requests import Session
from controller.websocket_controller import manager
from database.database import get_db
import yaml

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


################################### IDS and IPS Service #################################################


# Funzione per avviare IDS-IPS
def start_ids_ips():
    try:
        # Esegui il comando per avviare IDS-IPS
        subprocess.run(['/bin/ash', '/root/Defnet-IDS-IPS/./openwrt-ids-ips-production.sh', 'start'], check=True)
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


################################################## Parental Control Service ###################################################

def toggle_parental_control(file_path, enable):
    """
    Modifica il valore di `parental_enabled` in un file YAML.

    :param file_path: Percorso del file YAML.
    :param enable: Booleano, True per abilitare il controllo parentale, False per disabilitarlo.
    """
    try:
        # Legge il file YAML
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Modifica il valore di `parental_enabled`
        if 'filtering' in config and isinstance(config['filtering'], dict):
            config['filtering']['parental_enabled'] = enable
        else:
            print("Errore: Sezione 'filtering' non trovata o malformata.")
            return

        # Scrive il file YAML aggiornato
        with open(file_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        
        print(f"Configurazione aggiornata: `parental_enabled` impostato a {enable}.")
        
        subprocess.run(['service', 'adguardhome','restart'], check=True)

    except Exception as e:
        print(f"Errore durante la modifica del file YAML: {e}")





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


    if service_name == "Parental Control":
        if service_request.enabled:
            # Enable service 
            toggle_parental_control(file_path="/etc/adguardhome.yaml",enable=True)
        else:
            toggle_parental_control(file_path="/etc/adguardhome.yaml",enable=False)


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


# Recupera le informazioni in merito ai servizi che sono runnati sul router 
@router.get("/services", response_model=Dict[str, bool])
async def get_services_status():
    """
    Restituisce lo stato di tutti i servizi operativi.
    """
    try:
        return services_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero degli stati dei servizi: {e}")

