from datetime import datetime, timedelta
import time
import jwt
from jose import JWTError
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from models.users import User
from database.database import get_db

# Configurazione JWT
SECRET_KEY = "il_tuo_segreto_super_sicuro"  # Cambia questo valore con un segreto sicuro
ALGORITHM = "HS256"  # Algoritmo di hashing usato per i token JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # Endpoint per ottenere il token

# Aggiungi una blacklist per i token invalidati
blacklist = set()  # Una blacklist semplice (può essere un database in un'applicazione più complessa)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crea un token di accesso JWT.

    Args:
        data (dict): I dati da includere nel token.
        expires_delta (timedelta | None): La durata del token.

    Returns:
        str: Il token JWT codificato.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    print("Encoded JWT : "+encoded_jwt)
    return encoded_jwt

def verify_token_in_blacklist(token: str) -> bool:
    """
    Verifica se il token è presente nella blacklist.

    Args:
        token (str): Il token JWT.

    Returns:
        bool: True se il token è nella blacklist, False altrimenti.
    """
    return token in blacklist

def decode_token(token: str):
    """
    Decodifica un token JWT.

    Args:
        token (str): Il token JWT.

    Returns:
        dict: I payload del token decodificato.

    Raises:
        JWTError: Se il token è invalido o scaduto.
    """
    try:
        print("Token received !")
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM],options={"verify_signature": False})
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decoding token: {str(e)}")






def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Estrae l'utente attualmente autenticato utilizzando il token JWT.

    Args:
        token (str): Il token JWT fornito nel header Authorization.
        db (Session): Sessione del database.

    Returns:
        User: Istanza del modello utente autenticato.

    Raises:
        HTTPException: Se il token è invalido o l'utente non è trovato.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print("Stampa del Token : "+token)
        # Decodifica del token JWT
        payload = decode_token(token)
        username: str = payload.get("sub")  # Il campo 'sub' contiene il nome utente

        print("Stampa del Payload : "+payload)
        print("Stampa dell'username : "+username)
        
        if username is None:
            raise credentials_exception
        
        # Verifica se il token è presente nella blacklist
        if verify_token_in_blacklist(token):
            raise credentials_exception  # Token è invalidato, lo rifiutiamo

        # Verifica la data di scadenza (se presente nel token)
        if "exp" in payload and payload["exp"] < int(time.time()):
            raise credentials_exception  # Token scaduto

    except JWTError:
        raise credentials_exception

    # Recupero dell'utente dal database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
