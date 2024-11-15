from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from service.password_service import get_password_hash
from models.users import User



from controller.payload.response.registration_response import UserResponse
from controller.payload.request.registration_request import UserCreate


from fastapi import APIRouter

router = APIRouter()
    


# TODO : Definire un livello superiore
# Inserire il service per effettuare la registrazione dell'utente e farsi restituire True/False come risposta 
# Dal controller la risposta deve essere l'oggetto UserResponse con ID , Username , Password  
# Ricordare di cambiare l'IP del device nel file .env ( file di environment )   

# Utilizzare un parametro di input - UserCreate 
# Session risulta essere un parametro che prendono dal database per effettuare un sincronismo 

@router.post("/register", response_model=bool)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
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
        return True
    except:
        return False