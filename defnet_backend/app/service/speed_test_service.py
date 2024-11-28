import speedtest
import inspect

# services/speed_test_service.py
def get_speed_data():
    s = speedtest.Speedtest()
    
    # Trova il miglior server
    best_server = s.get_best_server()
    
    # Estrai il valore del ping dal server migliore
    latency = None
    for key, value in best_server.items():
        if key == "latency":
            latency = value  # Salva il valore della latenza

    # Ottieni velocità di download e upload
    download = s.download() / 1_000_000  # Converti a Mbps
    upload = s.upload() / 1_000_000  # Converti a Mbps
    
    # Crea il dizionario dei dati di velocità
    speed_data = {
        "download_speed": round(download, 2),  # Arrotonda a 2 decimali
        "upload_speed": round(upload, 2),
        "latency": round(latency, 2) if latency is not None else "N/A",  # Arrotonda la latenza
    }
    return speed_data