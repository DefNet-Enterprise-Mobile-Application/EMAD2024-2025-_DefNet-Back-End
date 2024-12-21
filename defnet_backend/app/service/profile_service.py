from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.users import User
from service.password_service import get_password_hash, verify_password
import logging

# Configurazione del logger (opzionale, ma utile in produzione)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_profile(user_id: int, new_username: str, current_password: str, new_password: str, db: Session) -> bool:
    """
    Aggiorna il profilo dell'utente, consentendo di modificare username e password.
    
    Args:
        user_id (int): ID dell'utente che vuole aggiornare il profilo.
        new_username (str): Nuovo username desiderato.
        current_password (str): Password attuale per l'autenticazione.
        new_password (str): Nuova password desiderata.
        db (Session): Sessione del database.

    Returns:
        bool: True se l'aggiornamento ha avuto successo, altrimenti viene sollevata un'eccezione.
    """
    
    # Recupero l'utente dal database
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verifica della password attuale
    if not verify_password(current_password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect current password")
    
   
    # Aggiorno la password se è stata fornita una nuova password
    if new_password == current_password:  # Non permetti di impostare la stessa password
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as current password")
    
    db_user.password_hash = get_password_hash(new_password)
    
    # Salvo le modifiche nel database
    db.commit()
    db.refresh(db_user)

    # Log delle modifiche al profilo
    logger.info(f"User profile updated: ID = {db_user.id}, Password update")  # Aggiungi un log

    return True
