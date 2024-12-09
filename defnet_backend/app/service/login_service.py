# login_service.py

from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.users import User
from controller.payload.request.login_request import LoginRequest

from service.password_service import verify_password

from service.jwt_service import create_access_token  # Importa la funzione dal file jwt_service
from service.jwt_service import ACCESS_TOKEN_EXPIRE_MINUTES,blacklist # Import CONFIGURATION SETTINGS JWT and BlackList 



def login_user(loginPayload: LoginRequest, db: Session):
    """
    Effettua il login dell'utente.

    Args:
        loginPayload (LoginRequest): I dati di login forniti dall'utente.
        db (Session): La sessione del database.

    Returns:
        dict: Il messaggio di successo e il token di accesso.

    Raises:
        HTTPException: Se l'username o la password sono errati.
    """
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
