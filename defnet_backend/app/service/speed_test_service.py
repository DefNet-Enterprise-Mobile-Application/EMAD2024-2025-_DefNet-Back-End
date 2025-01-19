import speedtest
import inspect

def get_download_speed():
    s = speedtest.Speedtest()
    # Ottieni la velocità di download in Mbps
    download = s.download() / 1_000_000  # Converti a Mbps
    return round(download, 2)

def get_upload_speed():
    s = speedtest.Speedtest()
    # Ottieni la velocità di upload in Mbps
    upload = s.upload() / 1_000_000  # Converti a Mbps
    return round(upload, 2)

def get_latency():
    s = speedtest.Speedtest()
    # Trova il miglior server
    best_server = s.get_best_server()
    
    # Estrai il valore del ping (latency) dal server migliore
    latency = best_server.get("latency", "N/A")  # Se non esiste, ritorna "N/A"
    
    if latency != "N/A":
        latency = round(latency, 2)  # Arrotonda la latenza a 2 decimali
    return latency