from fastapi import APIRouter
from app.service.speed_test_service import get_download_speed, get_latency, get_upload_speed

router = APIRouter()

@router.get("/speed-test")
async def fetch_speed_data():
    try:
        # Ottieni i valori da ciascun metodo del service
        download_speed = get_download_speed()
        upload_speed = get_upload_speed()
        latency = get_latency()
        
        # Log su console
        print(f"Download Speed: {download_speed} Mbps")
        print(f"Upload Speed: {upload_speed} Mbps")
        print(f"Latency: {latency} ms")
        
        # Restituisci i dati come JSON
        return {
            "success": True,
            "data": {
                "download_speed": download_speed,
                "upload_speed": upload_speed,
                "latency": latency
            }
        }
    except Exception as e:
        # Log dell'errore su console
        print(f"Errore durante il test di velocità: {e}")
        return {
            "success": False,
            "message": "Errore interno del server"
        }