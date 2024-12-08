from pydantic import BaseModel, Field

# Modello per la richiesta di cambio password
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8, description="The current password")
    new_password: str = Field(..., min_length=8, description="The new password")
    
    class Config:
        from_attributes = True  # Permette l'uso con ORM, utile se usi SQLAlchemy per la gestione dei dati