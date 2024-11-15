# General Import
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session



# Import from Service 
from service.password_service import  verify_password
# Import from Database 
from database.database import get_db
# Import from Models - User 
from models.users import User

# Import Payload - Request 
from controller.payload.request.login_request import LoginRequest


from fastapi import APIRouter

router = APIRouter()

# Endpoint di login con controlli specifici
# Utilizzare un oggetto LoginRequest - oggetto di Login per effettuare il Login 
# Oggetto Session - sincronizzazione del Db con oggetti ORM 

@router.post("/login")
def login(loginPayload: LoginRequest, db: Session = Depends(get_db)):
    # Controllo se l'utente esiste
    db_user = db.query(User).filter(User.username == loginPayload.username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username not found"
        )

    # Controllo della password
    if not verify_password(loginPayload.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Se username e password sono corretti
    return {"message": "Login successful!"}
