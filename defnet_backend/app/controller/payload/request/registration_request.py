from pydantic import BaseModel

# Oggetto Payload - User Registration  
class UserCreate(BaseModel):
    username: str
    password: str