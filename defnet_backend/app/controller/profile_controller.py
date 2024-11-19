from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.users import User
from database.database import get_db
from service.password_service import get_password_hash, verify_password  # Aggiungi queste importazioni

router = APIRouter()

# Endpoint per ottenere il profilo dell'utente
@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": db_user.username}

# Endpoint per aggiornare il profilo dell'utente
@router.put("/users/{user_id}/profile")
async def update_user_profile(
    user_id: int,
    username: str = None,
    current_password: str = None,
    new_password: str = None,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Controllo se l'utente sta cambiando la password
    if current_password and new_password:
        if not verify_password(current_password, db_user.password_hash):  # Usa verify_password per verificare la password
            raise HTTPException(status_code=400, detail="Incorrect password")
        db_user.password_hash = get_password_hash(new_password)  # Salva la nuova password hashata
    
    # Se c'è un nuovo username, controllo se è già preso
    if username and username != db_user.username:
        db_user_by_username = db.query(User).filter(User.username == username).first()
        if db_user_by_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        db_user.username = username  # Aggiorna l'username se disponibile

    # Salvo le modifiche nel database
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Profile updated successfully"}

