from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.users import User
from controller.payload.request.login_request import LoginRequest
from password_service import verify_password

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Se username e password sono corretti
    return {"message": "Login successful!"}