# General Import
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

# Import from Service 
from service.login_service import login_user

# Import from Database 
from database.database import get_db

# Import Payload - Request 
from controller.payload.request.login_request import LoginRequest


#Import funzione di jwt
from service.jwt_service import extract_username_from_token  

from fastapi import APIRouter

router = APIRouter()

# Endpoint di login con controlli specifici
# Utilizzare un oggetto LoginRequest - oggetto di Login per effettuare il Login 
# Oggetto Session - sincronizzazione del Db con oggetti ORM 
@router.post("/login")
def login(loginPayload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    try:
        result =  login_user(loginPayload, db)
        
        # Estrai l'username dal token generato
        access_token_data = result["access_token"]
        username = extract_username_from_token(access_token_data)

        # Recupera l'indirizzo IP del dispositivo
        client_ip = request.client.host
        

        # Ritorna il risultato del login
        return result
    
    except HTTPException as e:
        # Recupera l'indirizzo IP anche in caso di errore
        client_ip = request.client.host
        
        
        # Rilancia l'errore HTTPException per restituire il codice di stato 401 o altre informazioni
        raise e