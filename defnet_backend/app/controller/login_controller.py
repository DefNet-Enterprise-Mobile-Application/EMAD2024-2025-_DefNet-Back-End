# General Import
from fastapi import Depends
from sqlalchemy.orm import Session

# Import from Service 
from service.login_service import login_user

# Import from Database 
from database.database import get_db
# Import from Models - User 

# Import Payload - Request 
from controller.payload.request.login_request import LoginRequest


from fastapi import APIRouter

#import bcrypt #aggiunto io


router = APIRouter()

# Endpoint di login con controlli specifici
# Utilizzare un oggetto LoginRequest - oggetto di Login per effettuare il Login 
# Oggetto Session - sincronizzazione del Db con oggetti ORM 

@router.post("/login")
def login(loginPayload: LoginRequest, db: Session = Depends(get_db)):
    return login_user(loginPayload, db)
