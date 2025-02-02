from asyncio.log import logger
from fastapi import APIRouter, HTTPException
import os, subprocess
from service.wifi_settings_service import get_ssid, set_ssid, get_encryption, set_encryption, get_password, set_password, get_lan_ip
from qrcode.image.pil import PilImage
from service.wifi_settings_service import get_ssid, get_encryption, get_password
from io import BytesIO
import base64
from models.wifi_settings import WifiSettings
from fastapi import  HTTPException
import asyncio



router = APIRouter()

def get_wireless_interfaces():
    try:
        result = subprocess.run(['iwinfo'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        interfaces = []
        for line in lines:
            if 'ESSID' in line:
                interface = line.split()[0]
                interfaces.append(interface)
        return interfaces
    except Exception as e:
        print(f"Error getting wireless interfaces: {e}")
        return []

def get_connected_devices():
    devices = []
    try:
        result = subprocess.run(['ip', 'neigh'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                device = {
                    "ip": parts[0],
                    "mac": parts[4],
                    "interface": parts[2]
                }
                devices.append(device)
    except Exception as e:
        print(f"Error getting connected devices: {e}")
    return devices

def parse_dhcp_leases(file_path="/tmp/dhcp.leases"):
    leases = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    lease = {
                        "lease_time": parts[0],
                        "mac": parts[1],
                        "ip": parts[2],
                        "hostname": parts[3]
                    }
                    leases.append(lease)
    return leases

def get_network_stats():
    network_stats = {}
    for interface in os.listdir('/sys/class/net/'):
        stats_path = f"/sys/class/net/{interface}/statistics"
        if os.path.exists(stats_path):
            with open(os.path.join(stats_path, "tx_bytes"), "r") as f:
                tx_bytes = f.read().strip()
            with open(os.path.join(stats_path, "rx_bytes"), "r") as f:
                rx_bytes = f.read().strip()
            network_stats[interface] = {
                "tx_bytes": tx_bytes,
                "rx_bytes": rx_bytes
            }
    return network_stats

@router.get("/devices")
async def get_connected_devices_controller():
    try:
        # Ottieni le interfacce wireless
        wireless_interfaces = get_wireless_interfaces()

        # Leggere i lease DHCP
        dhcp_devices = parse_dhcp_leases()

        # Ottenere i dispositivi connessi
        arp_devices = get_connected_devices()

        # Ottenere statistiche di rete
        network_stats = get_network_stats()

        # Combinare le informazioni
        devices = []
        for dhcp_device in dhcp_devices:
            device_info = {
                "ip": dhcp_device["ip"],
                "mac": dhcp_device["mac"],
                "hostname": dhcp_device["hostname"],
                "interface": "unknown",
                "tx_bytes": "N/A",
                "rx_bytes": "N/A"
            }
            for arp_device in arp_devices:
                if dhcp_device["mac"] == arp_device["mac"]:
                    device_info["interface"] = arp_device["interface"]
                    break
            if device_info["interface"] in network_stats:
                device_info["tx_bytes"] = network_stats[device_info["interface"]].get("tx_bytes", "N/A")
                device_info["rx_bytes"] = network_stats[device_info["interface"]].get("rx_bytes", "N/A")
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
    
