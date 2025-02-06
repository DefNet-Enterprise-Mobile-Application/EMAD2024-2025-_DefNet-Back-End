from asyncio.log import logger
from fastapi import APIRouter, HTTPException
import os, subprocess
from service.wifi_settings_service import get_ssid, set_ssid, get_encryption, set_encryption, get_password, set_password, get_lan_ip
import qrcode
from qrcode.image.pil import PilImage
from service.wifi_settings_service import get_ssid, get_encryption, get_password
from io import BytesIO
import base64
from models.wifi_settings import WifiSettings
from fastapi import  HTTPException
import asyncio



router = APIRouter()

import subprocess
import os
from fastapi import HTTPException

import subprocess
import os
from fastapi import HTTPException

def get_assoclist(interface="phy1-ap0"):
    """ Ottiene la lista degli associati da iwinfo """
    assoclist = []
    try:
        result = subprocess.run(['iwinfo', interface, 'assoclist'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            # Estrai MAC address e RSSI
            if line:
                parts = line.split()
                mac = parts[0]
                rssi = parts[1] if len(parts) > 1 else "N/A"
                assoclist.append({
                    "mac": mac,
                    "rssi": rssi
                })
    except Exception as e:
        print(f"Error getting assoclist: {e}")
    return assoclist

def get_network_stats():
    """ Ottenere le statistiche di rete come tx/rx bytes per interfaccia """
    network_stats = {}
    for interface in os.listdir('/sys/class/net/'):
        stats_path = f"/sys/class/net/{interface}/statistics"
        if os.path.exists(stats_path):
            try:
                with open(os.path.join(stats_path, "tx_bytes"), "r") as f:
                    tx_bytes = f.read().strip()
                with open(os.path.join(stats_path, "rx_bytes"), "r") as f:
                    rx_bytes = f.read().strip()
                network_stats[interface] = {
                    "tx_bytes": tx_bytes,
                    "rx_bytes": rx_bytes
                }
            except Exception as e:
                print(f"Error reading network stats for {interface}: {e}")
    return network_stats

def get_device_name(ip):
    """ Cerca il nome del dispositivo dato l'indirizzo IP utilizzando il comando `getent` """
    try:
        result = subprocess.run(['getent', 'hosts', ip], capture_output=True, text=True)
        if result.returncode == 0:
            # Estrarre il nome host dall'output
            return result.stdout.split()[0]
    except Exception as e:
        print(f"Error getting device name for {ip}: {e}")
    return "Unknown"

@router.get("/devices")
async def get_connected_devices_controller():
    try:
        # Ottenere la lista degli associati (dispositivi connessi via Wi-Fi)
        assoclist_devices = get_assoclist()

        # Ottenere statistiche di rete (tx/rx bytes)
        network_stats = get_network_stats()

        # Combinare le informazioni dei dispositivi
        devices = []
        for assoc_device in assoclist_devices:
            device_info = {
                "mac": assoc_device["mac"],
                "rssi": assoc_device["rssi"],
                "interface": "unknown",  # L'interfaccia sarà identificata tramite le statistiche
                "tx_bytes": "N/A",
                "rx_bytes": "N/A",
                "hostname": "Unknown"  # Nome host inizialmente sconosciuto
            }

            # Aggiungere le statistiche di rete
            for interface in network_stats:
                if interface.startswith("phy1"):  # Associa l'interfaccia corretta, per esempio 'phy1-ap0'
                    device_info["interface"] = interface
                    device_info["tx_bytes"] = network_stats[interface].get("tx_bytes", "N/A")
                    device_info["rx_bytes"] = network_stats[interface].get("rx_bytes", "N/A")
                    break

            # Cerca il nome del dispositivo tramite l'IP (se disponibile)
            # Dato che i dispositivi connessi via Wi-Fi di solito hanno un IP sulla rete, potresti voler usare questo:
            device_info["hostname"] = get_device_name(device_info["mac"])  # Aggiungi il nome host, se disponibile

            devices.append(device_info)

        return {"connected_devices": devices}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







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
    
