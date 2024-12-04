
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.users import User
from controller.payload.request.registration_request import RegistrationRequest
from service.password_service import get_password_hash

def register_user(user: RegistrationRequest, db: Session) -> bool:

    # Controllo se l'username è già in uso
    db_user_by_username = db.query(User).filter(User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Controllo se l'email è già in uso
    db_user_by_email = db.query(User).filter(User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Creazione dell'utente con hashing della password
    new_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print("New user created:", new_user)  # Aggiungi un log per vedere i dati dell'utente
    return True
