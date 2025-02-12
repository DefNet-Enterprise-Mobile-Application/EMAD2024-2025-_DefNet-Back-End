from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from service.speed_test_service import get_download_speed, get_latency, get_upload_speed
from database.database import get_db
from models.speed_test import SpeedTest
router = APIRouter()

@router.get("/speed-test")
async def fetch_speed_data(db: Session = Depends(get_db)):
    try:
        print("Inizio ad effettuare lo speed-test .....")
        
        # Ottieni i valori dallo speed test
        download_speed = get_download_speed()
        upload_speed = get_upload_speed()
        latency = get_latency()

        # Log su console
        print(f"Download Speed: {download_speed} Mbps")
        print(f"Upload Speed: {upload_speed} Mbps")
        print(f"Latency: {latency} ms")

        # Salvataggio nel database
        speed_test_entry = SpeedTest(
            download_speed=download_speed,
            upload_speed=upload_speed,
            latency=latency
        )
        db.add(speed_test_entry)
        db.commit()
        db.refresh(speed_test_entry)

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
        print(f"Errore durante il test di velocità: {e}")
        return {
            "success": False,
            "message": "Errore interno del server"
        }
    


@router.get("/speed-test/latest")
async def get_latest_speed_test(db: Session = Depends(get_db)):
    try:
        latest_test = db.query(SpeedTest).order_by(SpeedTest.timestamp.desc()).first()
        
        if latest_test:
            return {
                "success": True,
                "data": {
                    "download_speed": latest_test.download_speed,
                    "upload_speed": latest_test.upload_speed,
                    "latency": latest_test.latency,
                    "timestamp": latest_test.timestamp
                }
            }
        else:
            return {
                "success": False,
                "message": "Nessun dato disponibile"
            }
    except Exception as e:
        print(f"Errore durante il recupero dei dati: {e}")
        return {
            "success": False,
            "message": "Errore interno del server"
        }
