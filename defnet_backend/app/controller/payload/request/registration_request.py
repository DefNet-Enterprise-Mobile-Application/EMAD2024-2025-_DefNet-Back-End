from pydantic import BaseModel, EmailStr

# Oggetto Payload - User Registration  
class RegistrationRequest(BaseModel):
    username: str
    password: str
    email : EmailStr