import speedtest

""" get_download_speed() - method to obtain the download speed of internet connection """
def get_download_speed():
    print("Sto facendo il recupero delle informazioni del download! ")
    s = speedtest.Speedtest()
    # Ottieni la velocità di download in Mbps
    download = s.download() / 1_000_000  # Converti a Mbps
    return round(download, 2)



""" get_upload_speed() - method to obtain how it is fast the upload internet connection """
def get_upload_speed():
    print("Sto facendo il recupero delle informazioni dell'upload! ")
    s = speedtest.Speedtest()
    # Ottieni la velocità di upload in Mbps
    upload = s.upload() / 1_000_000  # Converti a Mbps
    return round(upload, 2)



""" get_latency() - method to obtain latency of internet connection """
def get_latency():
    print("Sto facendo il recupero delle informazioni della Latenza! ")
    s = speedtest.Speedtest()
    # Trova il miglior server
    best_server = s.get_best_server()
    
    # Estrai il valore del ping (latency) dal server migliore
    latency = best_server.get("latency", "N/A")  # Se non esiste, ritorna "N/A"
    
    if latency != "N/A":
        latency = round(latency, 2)  # Arrotonda la latenza a 2 decimali
    return latency