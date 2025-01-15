from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from database.database import get_db
from models.users import User  # Importa il modello User dal file dove è definito

def get_user_by_id(db: Session, user_id: int):
    """
    Recupera un utente dal database dato il suo user_id.

    Args:
        db (Session): La sessione del database.
        user_id (int): L'ID dell'utente da cercare.

    Returns:
        User: Oggetto User se trovato, altrimenti lancia una HTTPException.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return user
