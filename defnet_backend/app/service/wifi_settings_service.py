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
        return {"status": "success", "message": f"{config_path} aggiornato con successo"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Errore durante l'aggiornamento di {config_path}: {str(e)}")




#### Get Wifi Settings Info ####
def get_ssid():
    return get_uci_value("wireless.@wifi-iface[0].ssid")


def get_encryption():
    raw_encryption = get_uci_value("wireless.@wifi-iface[0].encryption")
    return map_encryption_type(raw_encryption)

def get_password():
    return get_uci_value("wireless.@wifi-iface[0].key")

def get_lan_ip():
    return get_uci_value("network.lan.ipaddr")



######  Set Info about settings Network  ######

def set_encryption(new_encryption):
    raw_encryption = reverse_encryption_mapping(new_encryption)
    return set_uci_value("wireless.@wifi-iface[0].encryption", raw_encryption)

def set_ssid(new_ssid):
    return set_uci_value("wireless.@wifi-iface[0].ssid", new_ssid)

def set_password(new_password):
    return set_uci_value("wireless.@wifi-iface[0].key", new_password)







def map_encryption_type(encryption):
    encryption_mapping = {
        # WEP
        "wep": "WEP",
        "wep+open": "WEP",
        "wep+shared": "WEP",

        # WPA
        "psk": "WPA",
        "psk+ccmp": "WPA",
        "psk+aes": "WPA",
        "psk+tkip": "WPA",
        "psk+tkip+ccmp": "WPA",
        "psk+tkip+aes": "WPA",
        "psk-mixed": "WPA",
        "psk-mixed+ccmp": "WPA",
        "psk-mixed+aes": "WPA",
        "psk-mixed+tkip": "WPA",
        "psk-mixed+tkip+ccmp": "WPA",
        "psk-mixed+tkip+aes": "WPA",

        # WPA2
        "psk2": "WPA2",
        "psk2+ccmp": "WPA2",
        "psk2+aes": "WPA2",
        "psk2+tkip": "WPA2",
        "psk2+tkip+ccmp": "WPA2",
        "psk2+tkip+aes": "WPA2",

        # WPA3
        "sae": "WPA3",
        "sae-mixed": "WPA3",
        "wpa3": "WPA3",
        "wpa3-mixed": "WPA3",

        # Opportunistic Wireless Encryption (OWE)
        "owe": "WPA3",

        # Nessuna autenticazione
        "none": "None",
    }
    return encryption_mapping.get(encryption, "Unknown")


# Funzione di mapping inverso per la crittografia
def reverse_encryption_mapping(encryption_type):
    encryption_reverse_mapping = {
        "WEP": "wep",  # WEP
        "WPA": "psk",  # WPA (la modalità più semplice)
        "WPA2": "psk2",  # WPA2 (più sicuro di WPA)
        "WPA3": "sae",  # WPA3 (più sicuro di WPA2)
        "None": "none",  # Nessuna crittografia
    }
    # Restituisce il valore di crittografia più semplice disponibile
    return encryption_reverse_mapping.get(encryption_type, "none")



