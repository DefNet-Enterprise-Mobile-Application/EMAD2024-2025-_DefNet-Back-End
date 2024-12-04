from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.users import User
from dependencies import blacklist
from database.database import get_db
from service.password_service import get_password_hash, verify_password  # Aggiungi queste importazioni
from dependencies import get_current_user, oauth2_scheme
from service.profile_service import update_profile
from models.passwordRequest import ChangePasswordRequest


router = APIRouter()

# Endpoint dedicato al cambio della password
@router.put("/users/{user_id}/change-password")
async def change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Autenticazione tramite token
    token: str = Depends(oauth2_scheme)
):
    # Verifica che l'utente stia cambiando la propria password
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Operation not allowed")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verifica della password corrente
    if not verify_password(payload.current_password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Verifica che la nuova password sia diversa
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the current password")

     # Usa il servizio per aggiornare la password
    try:
        # Modifica la password tramite il servizio
        update_profile(user_id=user_id, new_username=None, current_password=payload.current_password, new_password=payload.new_password, db=db)

        # Invalida il vecchio token (aggiungendolo alla blacklist)
        #token = payload.token  # Recupera il token dell'utente corrente
        blacklist.add(token)  # Aggiungi il token alla blacklist per invalidarlo

    except HTTPException as e:
        raise e  # Rilancia l'eccezione se qualcosa va storto

    return {"message": "Password updated successfully"}
   
