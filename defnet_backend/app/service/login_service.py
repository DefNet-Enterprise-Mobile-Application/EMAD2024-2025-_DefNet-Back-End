from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.users import User
from controller.payload.request.login_request import LoginRequest
from service.password_service import verify_password
from datetime import datetime, timedelta
import jwt
from dependencies import blacklist

# Configurazione JWT
SECRET_KEY = "il_tuo_segreto_super_sicuro"  # Cambialo con un valore sicuro
ALGORITHM = "HS256"  # Algoritmo di hashing
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tempo di scadenza del token in minuti

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_user(loginPayload: LoginRequest, db: Session):
    # Controllo se l'utente esiste
    db_user = db.query(User).filter(User.username == loginPayload.username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username not found"
        )

    # Controllo della password
    if not verify_password(loginPayload.password, db_user.password_hash):
        print("Password mismatch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Se username e password sono corretti
     # Se login ha successo, genera un JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": db_user.username,
            "user_id": db_user.id,
            "email": db_user.email 
        },
        expires_delta=access_token_expires
    )
    
    # Se l'utente ha cambiato la password, invalidiamo il token precedente (assicurandoci che il token precedente sia nella blacklist)
    if hasattr(db_user, 'previous_token') and db_user.previous_token:
        blacklist.add(db_user.previous_token)
        
    # Aggiorna il token precedente nell'utente (opzionale)
    db_user.previous_token = access_token
    
    print("Login successful")
    return {
        "message": "Login successful!",
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Durata del token in secondi
    }
  