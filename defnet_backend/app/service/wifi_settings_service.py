import subprocess

# Servizio per ottenere un valore UCI
def get_uci_value(config_path):
    try:
        result = subprocess.run(['uci', 'get', config_path], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Errore durante il recupero di {config_path}: {str(e)}")

# Servizio per impostare un valore UCI
def set_uci_value(config_path, value):
    try:
        subprocess.run(['uci', 'set', f'{config_path}={value}'], check=True)
        subprocess.run(['uci', 'commit'], check=True)
        subprocess.run(['wifi'], check=True)  # Ricarica le configurazioni Wi-Fi
        return {"status": "success", "message": f"{config_path} aggiornato con successo"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Errore durante l'aggiornamento di {config_path}: {str(e)}")

# Servizi specifici
def get_ssid():
    return get_uci_value("wireless.@wifi-iface[1].ssid")

def set_ssid(new_ssid):
    return set_uci_value("wireless.@wifi-iface[1].ssid", new_ssid)

def get_encryption():
    return get_uci_value("wireless.@wifi-iface[1].encryption")

def set_encryption(new_encryption):
    return set_uci_value("wireless.@wifi-iface[1].encryption", new_encryption)

def get_password():
    return get_uci_value("wireless.@wifi-iface[1].key")

def set_password(new_password):
    return set_uci_value("wireless.@wifi-iface[1].key", new_password)

def get_lan_ip():
    return get_uci_value("network.lan.ipaddr")
