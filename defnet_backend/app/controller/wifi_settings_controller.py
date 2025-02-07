from asyncio.log import logger
from fastapi import APIRouter, HTTPException
import subprocess

from fastapi.responses import JSONResponse
from flask import jsonify
from service.wifi_settings_service import get_ssid, set_ssid, get_encryption, set_encryption, get_password, set_password, get_lan_ip
import qrcode
from qrcode.image.pil import PilImage
from io import BytesIO
import base64

from models.wifi_settings import WifiSettings
from fastapi import  HTTPException
import asyncio
import re

router = APIRouter()

def get_connected_macs():
    """
    Esegue il comando 'iwinfo phy1-ap0 assoclist' per ottenere i MAC dei dispositivi connessi.
    Restituisce una lista di MAC (in minuscolo).
    """
    try:
        output = subprocess.check_output(["iwinfo", "phy1-ap0", "assoclist"], text=True)
    except subprocess.CalledProcessError as e:
        logger.error("Errore durante l'esecuzione di iwinfo: %s", e)
        return []
    
    # Utilizza una regex per trovare gli indirizzi MAC
    mac_pattern = re.compile(r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})")
    macs = mac_pattern.findall(output)
    
    # Rimuove duplicati e normalizza in minuscolo
    return list(set(mac.lower() for mac in macs))

def get_dhcp_leases(leases_file="/tmp/dhcp.leases"):
    """
    Legge il file dei lease DHCP e crea un dizionario indicizzato per MAC.
    Il file dovrebbe avere il formato:
      <timestamp> <MAC> <IP> <nome_host> <client_id>
    """
    leases = {}
    try:
        with open(leases_file, "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 5:
                    timestamp, mac, ip, hostname, client_id = parts[:5]
                    leases[mac.lower()] = {
                        "timestamp": timestamp,
                        "ip": ip,
                        "hostname": hostname,
                        "client_id": client_id
                    }
    except FileNotFoundError:
        logger.error("Il file %s non è stato trovato.", leases_file)
    return leases

@router.get('/connected-devices')
def get_connected_devices():
    """
    Endpoint per ottenere i dispositivi attualmente connessi.
    Per ciascun MAC trovato con 'iwinfo phy1-ap0 assoclist', cerca nel file DHCP (/tmp/dhcp.leases)
    le informazioni (IP, hostname). Se non viene trovato il lease, viene indicato un errore.
    Inoltre, per completezza, vengono inseriti dei placeholder per 'tx_bytes' e 'rx_bytes'.
    """
    connected_macs = get_connected_macs()
    dhcp_leases = get_dhcp_leases()

    devices = []
    for mac in connected_macs:
        device_info = {"mac": mac}
        if mac in dhcp_leases:
            lease = dhcp_leases[mac]
            device_info["ip"] = lease["ip"]
            device_info["hostname"] = lease["hostname"]
        else:
            device_info["error"] = "Nessun lease DHCP trovato (dispositivo con IP statico o lease scaduto)"
        
        # Poiché non abbiamo parsato dati TX/RX dall'output di iwinfo, utilizziamo valori di default
        device_info["tx_bytes"] = "0"
        device_info["rx_bytes"] = "0"

        devices.append(device_info)
    
    # Restituisci la lista dei dispositivi in un dizionario con chiave 'connected_devices'
    return JSONResponse(content={"connected_devices": devices})



@router.get("/wifi/settings")
async def get_wifi_settings():
    """
    Recupera le impostazioni Wi-Fi (SSID, encryption, password e IP del gateway LAN).
    """
    try:
        ssid = get_ssid()
        encryption = get_encryption()
        password = get_password()
        lan_ip = get_lan_ip()
        return {
            "ssid": ssid,
            "encryption": encryption,
            "password": password,
            "lan_ip": lan_ip
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.put("/wifi/settings")
async def update_wifi_settings(settings: WifiSettings):
    """
    Modifica le impostazioni Wi-Fi senza bloccare la connessione HTTP.
    Invia una notifica all'utente tramite WebSocket.
    """

    # Funzione asincrona che gestisce le modifiche alle impostazioni Wi-Fi
    async def apply_settings():
        try:
            # Invia una notifica all'utente che l'operazione sta iniziando

            # Aggiorna SSID
            set_ssid(settings.ssid)
            # Aggiorna la modalità di crittografia
            set_encryption(settings.encryption)
            # Aggiorna la password Wi-Fi
            set_password(settings.password)
            # Commit e ricarica Wi-Fi
            subprocess.run(['uci', 'commit'], check=True)
            subprocess.run(['wifi'], check=True)  # Ricarica le configurazioni Wi-Fi

            # Dopo l'aggiornamento, invia una notifica che l'operazione è stata completata

        except Exception as e:
            logger.error(f"Errore durante l'applicazione delle impostazioni Wi-Fi: {str(e)}")
            # Notifica l'utente dell'errore

    # Avvia il processo di applicazione delle impostazioni Wi-Fi come task asincrono
    asyncio.create_task(apply_settings())

    # Rispondi immediatamente al client indicando che l'operazione è in corso
    return {"status": "pending", "message": "Le impostazioni Wi-Fi sono in fase di aggiornamento. La connessione verra\' interrotta. Riconnettiti al Wi-Fi appena disponibile."}

def generate_wifi_qr(ssid: str, encryption: str, password: str):
    wifi_string = f"WIFI:T:{encryption};S:{ssid};P:{password};;"
    qr = qrcode.make(wifi_string)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

@router.get("/wifi/qr")
async def get_wifi_qr():
    """
    Genera un QR code per la rete Wi-Fi basato sulle impostazioni attuali.
    """
    try:
        ssid = get_ssid()
        encryption = get_encryption()
        password = get_password()

        if not ssid or not encryption or not password:
            raise HTTPException(status_code=400, detail="Impossibile ottenere le impostazioni Wi-Fi")

        qr_code_base64 = generate_wifi_qr(ssid, encryption, password)
        print(qr_code_base64)
        return {"qr_code": qr_code_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# Controlla tale metodo per l'inserimento dei dati di mock del tuo wifi 
@router.get("/wifi/qr_test")
async def get_wifi_qr_test():
    """
    Genera un QR code per la rete Wi-Fi basato sulle impostazioni attuali.
    """
    try:
        ssid = get_ssid() # Modifica con il tuo SSID
        encryption = get_encryption() # Modfifica la tua encryption
        password = get_password() # Modifica della password 

        if not ssid or not encryption or not password:
            raise HTTPException(status_code=400, detail="Impossibile ottenere le impostazioni Wi-Fi")

        qr_code_base64 = generate_wifi_qr(ssid, encryption, password)
        print(qr_code_base64)
        return {"qr_code": qr_code_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
