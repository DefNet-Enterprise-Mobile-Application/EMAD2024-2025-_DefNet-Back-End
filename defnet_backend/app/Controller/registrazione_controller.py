from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from database.database import get_db, Base
from service.password_service import get_password_hash , verify_password
from models.users import User



from controller.payload.response.registration_response import UserResponse
from controller.payload.request.registration_request import UserCreate


from fastapi import APIRouter

router = APIRouter()
    
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Controllo se l'username è già in uso
    db_user_by_username = db.query(User).filter(User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Creazione dell'utente con hashing della password
    new_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print("New user created:", new_user)  # Aggiungi un log per vedere i dati dell'utente
    return new_user