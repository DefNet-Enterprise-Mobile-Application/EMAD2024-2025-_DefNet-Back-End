from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from service.jwt_service import blacklist
from service.jwt_service import oauth2_scheme,get_current_user
from database.database import get_db

router = APIRouter()

# Endpoint di logout
@router.post("/logout")
async def logout(authorization: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decodifica del token e verifica se l'utente esiste nel database
        #user = get_current_user(token=authorization, db=db)

        #if user:
            # Aggiungi il token alla blacklist
        blacklist.add(authorization)
          #  return {"message": "Logged out successfully."}
        #  else:
        #     raise HTTPException(status_code=401, detail="User not found")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code = 500, detail="Error logging out")