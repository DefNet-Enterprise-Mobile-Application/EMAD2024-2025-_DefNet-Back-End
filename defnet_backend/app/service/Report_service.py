from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.users import User

class ReportService:
    def get_daily_report(user_id: int, db: Session):
        users = db.query(User).all()
        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        # Converti ogni utente in un dizionario, escludendo _sa_instance_state
        users_data = [{key: value for key, value in user.__dict__.items() if key != "_sa_instance_state"} for user in users]

        # Stampa tutti gli utenti (solo per debug)
        for user_data in users_data:
            print(user_data)
        
        return users_data
