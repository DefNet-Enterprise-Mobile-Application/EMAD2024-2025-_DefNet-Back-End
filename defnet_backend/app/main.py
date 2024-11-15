from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurazione del database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Contesto per l'hashing delle password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modello del database per gli utenti
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    
class UserResponse(BaseModel):
    id : int
    username: str
    
class UserCreate(BaseModel):
    username: str
    password: str


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funzioni per la gestione delle password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Schema per il login
class Login(BaseModel):
    username: str
    password: str


# Endpoint di login con controlli specifici
@app.post("/login")
def login(login: Login, db: Session = Depends(get_db)):
    # Controllo se l'utente esiste
    db_user = db.query(User).filter(User.username == login.username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username not found"
        )

    # Controllo della password
    if not verify_password(login.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Se username e password sono corretti
    return {"message": "Login successful!"}